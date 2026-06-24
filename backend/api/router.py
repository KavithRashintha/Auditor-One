import asyncio
import json
import re
import sys
import time
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from pydantic import TypeAdapter

from backend.models.dto import AuditRequest, RecommendationDTO
from backend.security.ssrf import validate_url
from backend.scraper.harvester import SelectolaxPageHarvester
from backend.scraper.dom_lexer import DOMLexer
from backend.heuristics.engine import evaluate_heuristics, AGENCY_RULES
from backend.prompts.compiler import build_system_prompt, build_user_prompt
from backend.llm.factory import get_llm_orchestrator
from backend.logging.local_disk import LocalDiskTraceRepository
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1")

def _log(msg: str):
    """Unbuffered log to stderr for real-time visibility in terminal."""
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

@router.post("/audit")
async def audit_endpoint(request: AuditRequest):
    async def event_generator():
        pipeline_start = time.perf_counter()
        _log(f"\n{'='*60}")
        _log(f"[AUDIT START] URL: {request.url}")
        _log(f"{'='*60}")

        try:
            # 1. SSRF validate URL
            _log(f"[STAGE 1] SSRF validation...")
            try:
                validate_url(request.url)
                _log(f"[STAGE 1] ✓ SSRF validation passed")
            except HTTPException as e:
                _log(f"[STAGE 1] ✗ SSRF validation failed: {e.detail}")
                yield ServerSentEvent(event="error", data=json.dumps({"stage": "SSRF", "message": e.detail}))
                return

            # 2. Harvest Metrics
            _log(f"[STAGE 2] Harvesting page...")
            t = time.perf_counter()
            harvester = SelectolaxPageHarvester()
            try:
                metrics, raw_html = await harvester.harvest(request.url)
                _log(f"[STAGE 2] ✓ Harvested in {(time.perf_counter()-t)*1000:.0f}ms | HTML size: {len(raw_html)} chars")
            except HTTPException as e:
                _log(f"[STAGE 2] ✗ Harvest HTTPException: {e.detail}")
                yield ServerSentEvent(event="error", data=json.dumps({"stage": "SCRAPE", "message": e.detail}))
                return
            except Exception as e:
                _log(f"[STAGE 2] ✗ Harvest exception: {e}")
                yield ServerSentEvent(event="error", data=json.dumps({"stage": "SCRAPE", "message": f"Harvest failed: {str(e)}"}))
                return

            # 3. Yield Metrics
            _log(f"[STAGE 3] Yielding metrics event...")
            yield ServerSentEvent(event="metrics", data=metrics.model_dump_json())
            _log(f"[STAGE 3] ✓ Metrics yielded")

            # 4. Lex DOM
            _log(f"[STAGE 4] Lexing DOM...")
            t = time.perf_counter()
            lexer = DOMLexer()
            dom_markdown = lexer.lex(raw_html)
            _log(f"[STAGE 4] ✓ DOM lexed in {(time.perf_counter()-t)*1000:.0f}ms | Markdown size: {len(dom_markdown)} chars")

            # 5. Evaluate Heuristics
            _log(f"[STAGE 5] Evaluating heuristics...")
            heuristics = evaluate_heuristics(metrics, AGENCY_RULES)
            _log(f"[STAGE 5] ✓ Heuristics fired: {len(heuristics)} rules")

            # 6. Build Prompts
            _log(f"[STAGE 6] Building prompts...")
            system_prompt = build_system_prompt()
            user_prompt = build_user_prompt(metrics, dom_markdown, heuristics)
            _log(f"[STAGE 6] ✓ System prompt: {len(system_prompt)} chars | User prompt: {len(user_prompt)} chars")

            # 7. LLM Orchestrator
            _log(f"[STAGE 7] Starting LLM stream (provider: {__import__('backend.config', fromlist=['settings']).settings.LLM_PROVIDER})...")
            orchestrator = get_llm_orchestrator()
            
            full_response_buffer = ""
            json_accumulator = ""
            is_json_mode = False
            chunk_count = 0

            DELIMITER = "---REC_SPLIT---"
            yield_buffer = ""

            t = time.perf_counter()
            try:
                async for chunk in orchestrator.audit_stream(system_prompt, user_prompt):
                    chunk_count += 1
                    if chunk_count == 1:
                        _log(f"[STAGE 7] ✓ First token received after {(time.perf_counter()-t)*1000:.0f}ms")
                    if chunk_count % 50 == 0:
                        _log(f"[STAGE 7] ... {chunk_count} chunks received, buffer: {len(full_response_buffer)} chars")

                    full_response_buffer += chunk

                    if not is_json_mode:
                        yield_buffer += chunk
                        
                        if DELIMITER in yield_buffer:
                            is_json_mode = True
                            _log(f"[STAGE 7] ✓ Delimiter found at chunk #{chunk_count}. Switching to JSON mode.")
                            parts = yield_buffer.split(DELIMITER)
                            if parts[0]:
                                yield ServerSentEvent(event="insight_chunk", data=json.dumps(parts[0]))
                            
                            json_accumulator += parts[1]
                        else:
                            safe_to_yield = yield_buffer
                            for i in range(1, len(DELIMITER) + 1):
                                if yield_buffer.endswith(DELIMITER[:i]):
                                    safe_to_yield = yield_buffer[:-i]
                                    break
                            
                            if safe_to_yield:
                                yield ServerSentEvent(event="insight_chunk", data=json.dumps(safe_to_yield))
                                yield_buffer = yield_buffer[len(safe_to_yield):]
                    else:
                        json_accumulator += chunk

                _log(f"[STAGE 7] ✓ LLM stream complete. Total chunks: {chunk_count}, Total chars: {len(full_response_buffer)}")
                if not is_json_mode:
                    _log(f"[STAGE 7] ⚠ WARNING: Delimiter '{DELIMITER}' was NEVER found in the LLM output!")
                    _log(f"[STAGE 7] LLM output preview:\n{full_response_buffer[:500]}")

            except Exception as e:
                _log(f"[STAGE 7] ✗ LLM stream exception: {e}")
                yield ServerSentEvent(event="error", data=json.dumps({"stage": "LLM", "message": f"LLM stream failed: {str(e)}"}))
                return

            # 8. Extract Recommendations
            _log(f"[STAGE 8] Parsing recommendations JSON (accumulator size: {len(json_accumulator)} chars)...")
            recommendations_data = []
            
            try:
                clean_json = json_accumulator.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()
                
                raw_recs = json.loads(clean_json)
                recommendations = TypeAdapter(list[RecommendationDTO]).validate_python(raw_recs)
                recommendations_data = [r.model_dump() for r in recommendations]
                _log(f"[STAGE 8] ✓ Parsed {len(recommendations_data)} recommendations")
            except Exception as parse_err:
                _log(f"[STAGE 8] ⚠ Primary JSON parse failed: {parse_err}. Trying regex fallback...")
                try:
                    match = re.search(r'\[\s*\{.*\}\s*\]', full_response_buffer, re.DOTALL)
                    if match:
                        raw_recs = json.loads(match.group(0))
                        recommendations = TypeAdapter(list[RecommendationDTO]).validate_python(raw_recs)
                        recommendations_data = [r.model_dump() for r in recommendations]
                        _log(f"[STAGE 8] ✓ Regex fallback parsed {len(recommendations_data)} recommendations")
                    else:
                        _log(f"[STAGE 8] ✗ Regex fallback found no JSON array")
                except Exception as fallback_e:
                    _log(f"[STAGE 8] ✗ Fallback parsing also failed: {fallback_e}")

            if recommendations_data:
                for idx, r in enumerate(recommendations_data, start=1):
                    r["priority"] = idx

            yield ServerSentEvent(event="recommendations", data=json.dumps(recommendations_data))
            
            # 8.5 Save trace to repository
            try:
                trace_id = str(uuid.uuid4())
                trace = {
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "target_url": request.url,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "raw_llm_output": full_response_buffer,
                    "scraped_metrics": metrics.model_dump(),
                    "heuristics_fired": heuristics,
                    "recommendations": recommendations_data
                }
                repo = LocalDiskTraceRepository()
                saved_path = await repo.save(trace)
                _log(f"[STAGE 9] ✓ Trace saved to: {saved_path}")
                
                yield ServerSentEvent(event="prompt_log_meta", data=json.dumps({
                    "trace_id": trace_id,
                    "path": saved_path
                }))
            except Exception as trace_err:
                _log(f"[STAGE 9] ✗ Failed to save trace: {trace_err}")

            # 9. Done
            total_elapsed = (time.perf_counter() - pipeline_start) * 1000
            _log(f"\n[AUDIT COMPLETE] Total elapsed: {total_elapsed:.0f}ms")
            _log(f"{'='*60}\n")
            yield ServerSentEvent(event="done", data=json.dumps({}))

        except Exception as e:
            _log(f"[AUDIT FATAL] Unhandled exception: {e}")
            yield ServerSentEvent(event="error", data=json.dumps({"stage": "GENERAL", "message": str(e)}))

    return EventSourceResponse(event_generator())


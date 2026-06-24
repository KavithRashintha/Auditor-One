import asyncio
import json
import re
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

@router.post("/audit")
async def audit_endpoint(request: AuditRequest):
    async def event_generator():
        try:
            # 1. SSRF validate URL
            try:
                validate_url(request.url)
            except ValueError as e:
                yield ServerSentEvent(event="error", data=json.dumps({"stage": "SSRF", "message": str(e)}))
                return

            # 2. Harvest Metrics
            harvester = SelectolaxPageHarvester()
            try:
                metrics, raw_html = await harvester.harvest(request.url)
            except HTTPException as e:
                yield ServerSentEvent(event="error", data=json.dumps({"stage": "SCRAPE", "message": e.detail}))
                return
            except Exception as e:
                yield ServerSentEvent(event="error", data=json.dumps({"stage": "SCRAPE", "message": f"Harvest failed: {str(e)}"}))
                return

            # 3. Yield Metrics
            yield ServerSentEvent(event="metrics", data=metrics.model_dump_json())

            # 4. Lex DOM
            lexer = DOMLexer()
            dom_markdown = lexer.lex(raw_html)

            # 5. Evaluate Heuristics
            heuristics = evaluate_heuristics(metrics, AGENCY_RULES)

            # 6. Build Prompts
            system_prompt = build_system_prompt()
            user_prompt = build_user_prompt(metrics, dom_markdown, heuristics)

            # 7. LLM Orchestrator
            orchestrator = get_llm_orchestrator()
            
            full_response_buffer = ""
            json_accumulator = ""
            is_json_mode = False

            DELIMITER = "---REC_SPLIT---"
            yield_buffer = ""

            try:
                async for chunk in orchestrator.audit_stream(system_prompt, user_prompt):
                    full_response_buffer += chunk

                    if not is_json_mode:
                        yield_buffer += chunk
                        
                        if DELIMITER in yield_buffer:
                            is_json_mode = True
                            parts = yield_buffer.split(DELIMITER)
                            if parts[0]:
                                yield ServerSentEvent(event="insight_chunk", data=json.dumps(parts[0]))
                            
                            json_accumulator += parts[1]
                        else:
                            # Safe yielding to avoid partial delimiters slipping through
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
            except Exception as e:
                yield ServerSentEvent(event="error", data=json.dumps({"stage": "LLM", "message": f"LLM stream failed: {str(e)}"}))
                return

            # 8. Extract Recommendations
            recommendations_data = []
            
            try:
                # Remove markdown json code blocks if present
                clean_json = json_accumulator.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()
                
                raw_recs = json.loads(clean_json)
                recommendations = TypeAdapter(list[RecommendationDTO]).validate_python(raw_recs)
                recommendations_data = [r.model_dump() for r in recommendations]
            except Exception:
                # Fallback Regex
                try:
                    match = re.search(r'\[\s*\{.*\}\s*\]', full_response_buffer, re.DOTALL)
                    if match:
                        raw_recs = json.loads(match.group(0))
                        recommendations = TypeAdapter(list[RecommendationDTO]).validate_python(raw_recs)
                        recommendations_data = [r.model_dump() for r in recommendations]
                except Exception as fallback_e:
                    print("Fallback parsing failed:", fallback_e)

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
                
                # Yield meta event
                yield ServerSentEvent(event="prompt_log_meta", data=json.dumps({
                    "trace_id": trace_id,
                    "path": saved_path
                }))
            except Exception as trace_err:
                print(f"Failed to save trace: {trace_err}")

            # 9. Yield done
            yield ServerSentEvent(event="done", data=json.dumps({}))

        except Exception as e:
            yield ServerSentEvent(event="error", data=json.dumps({"stage": "GENERAL", "message": str(e)}))

    return EventSourceResponse(event_generator())

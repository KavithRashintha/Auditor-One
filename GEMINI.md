# Project Memory

## Status

- **Phase**: Planning Complete — Awaiting Execution Approval
- **Last Updated**: 2026-06-24T15:21:23+05:30

## Completed Endpoints / Features

- ✅ Rules Loaded
- ✅ Implementation Plan Created (13 milestones)
- ✅ M1: Project Scaffolding & Config
- ✅ M2: Data Contracts & Pydantic Models
- ✅ M3: SSRF Security Layer
- ✅ M4: Deterministic Harvester (Layer 2)
- ✅ M5: DOM Lexer & Token Hard-Cap (Layer 3)
- ✅ M6: Agency Heuristics Engine (Layer 3.5)
- ✅ M7: SSE Gateway (Mock Mode, Stage 2)
- ✅ M8: React SPA Shell & SSE Client
- ✅ M9: LLM Orchestrator & Stream Splitter (Stage 3)

## Known Decisions

- **Stack**: FastAPI (Python 3.11+) + React 18 (Vite, TypeScript, TailwindCSS) — per spec
- **Parser**: selectolax (C-parser) over BeautifulSoup4 — per spec timing SLA < 1000ms
- **SSE Client**: fetch() + ReadableStream — EventSource forbidden (GET-only by HTML5 spec)
- **Harvester return**: tuple (ScrapedMetricsDTO, raw_html) to feed both metrics layer and DOM Lexer
- **LLM Default**: OpenAI as primary; Anthropic wired via Strategy pattern
- **Token Cap**: 12,800 chars (~3,200 tokens) truncation on DOM Markdown output
- **Logging**: Async disk write via LocalDiskTraceRepository to LOG_DIR after LLM completes

## Environment Variables Required

- OPENAI_API_KEY (required)
- LLM_PROVIDER: "openai" | "anthropic" (required)
- FRONTEND_URL: CORS allowed origin (required)
- LOG_DIR: path for reasoning trace JSON files (required)
- ANTHROPIC_API_KEY (conditional — only if LLM_PROVIDER=anthropic)

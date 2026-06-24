import asyncio
import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from backend.models.dto import (
    AuditRequest,
    ScrapedMetricsDTO,
    HeadingsDTO,
    LinksDTO,
    ImagesDTO,
    MetadataDTO
)

router = APIRouter(prefix="/api/v1")

@router.post("/audit")
async def audit_endpoint(request: AuditRequest):
    async def event_generator():
        # Yield mock metrics
        metrics = ScrapedMetricsDTO(
            word_count=450,
            headings=HeadingsDTO(h1=1, h2=3, h3=5),
            links=LinksDTO(internal=12, external=4),
            cta_count=2,
            images=ImagesDTO(total=5, missing_alt=1, missing_alt_percentage=20.0),
            metadata=MetadataDTO(title="Mock Title", description="Mock Description")
        )
        yield ServerSentEvent(event="metrics", data=metrics.model_dump_json())

        # Yield 10x mock insight chunks
        dummy_chunks = [
            "This ", "is ", "a ", "mock ", "insight ", "stream. ",
            "The ", "real ", "LLM ", "will ", "be ", "connected ", "later."
        ]
        
        # We need 10 items to strictly follow the "10x" mock insight chunks requirement
        if len(dummy_chunks) > 10:
            dummy_chunks = dummy_chunks[:10]
        else:
            while len(dummy_chunks) < 10:
                dummy_chunks.append("... ")
                
        for chunk in dummy_chunks:
            await asyncio.sleep(0.1)
            yield ServerSentEvent(event="insight_chunk", data=json.dumps(chunk))

        # Yield done
        yield ServerSentEvent(event="done", data=json.dumps({}))

    return EventSourceResponse(event_generator())

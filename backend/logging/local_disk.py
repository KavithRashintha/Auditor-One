import json
import os
import asyncio
from typing import Any
from backend.config import settings
from backend.logging.base import ReasoningTraceRepository

class LocalDiskTraceRepository(ReasoningTraceRepository):
    def __init__(self):
        self.log_dir = settings.LOG_DIR
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def _save_sync(self, trace: dict[str, Any], filepath: str) -> str:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trace, f, indent=2, ensure_ascii=False)
        return filepath

    async def save(self, trace: dict[str, Any]) -> str:
        timestamp_iso = trace.get("timestamp", "unknown_time").replace(":", "-")
        filename = f"reasoning_trace_{timestamp_iso}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        # Run the synchronous file write in a separate thread so it doesn't block the event loop
        return await asyncio.to_thread(self._save_sync, trace, filepath)

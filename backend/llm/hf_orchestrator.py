from typing import AsyncGenerator
from openai import AsyncOpenAI
from backend.config import settings
from backend.llm.base import BaseLLMOrchestrator
import sys

def _log(msg: str):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

class HFLLMOrchestrator(BaseLLMOrchestrator):
    def __init__(self):
        self.model = settings.HF_MODEL or "mistralai/Mistral-7B-Instruct-v0.2"
        
        base_url = settings.HF_ENDPOINT
        # Auto-construct from model name if endpoint is missing or contains unresolved vars
        if not base_url or "${" in base_url:
            base_url = f"https://router.huggingface.co/v1"
        
        # Only append /v1 if not already present
        if not base_url.rstrip("/").endswith("/v1"):
            base_url = f"{base_url.rstrip('/')}/v1"

        _log(f"[HF] base_url={base_url} model={self.model}")
            
        self.client = AsyncOpenAI(
            api_key=settings.HF_API_TOKEN,
            base_url=base_url,
            timeout=120.0,
        )

    async def audit_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=True,
            temperature=0.2,
            max_tokens=4096
        )
        
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content


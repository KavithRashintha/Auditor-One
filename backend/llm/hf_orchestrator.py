from typing import AsyncGenerator
from openai import AsyncOpenAI
from backend.config import settings
from backend.llm.base import BaseLLMOrchestrator

class HFLLMOrchestrator(BaseLLMOrchestrator):
    def __init__(self):
        base_url = settings.HF_ENDPOINT
        if base_url and not base_url.endswith("/v1"):
            base_url = f"{base_url.rstrip('/')}/v1"
            
        self.client = AsyncOpenAI(
            api_key=settings.HF_API_TOKEN,
            base_url=base_url
        )
        self.model = settings.HF_MODEL or "mistralai/Mistral-7B-Instruct-v0.2"

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

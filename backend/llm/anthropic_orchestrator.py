from typing import AsyncGenerator
from anthropic import AsyncAnthropic
from backend.config import settings
from backend.llm.base import BaseLLMOrchestrator

class AnthropicOrchestrator(BaseLLMOrchestrator):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-haiku-20240307" # Using a fast default model

    async def audit_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        stream = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            stream=True,
            temperature=0.2,
            max_tokens=4000
        )
        
        async for event in stream:
            if event.type == "content_block_delta":
                yield event.delta.text

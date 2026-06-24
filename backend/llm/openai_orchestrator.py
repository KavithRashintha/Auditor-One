from typing import AsyncGenerator
from openai import AsyncOpenAI
from backend.config import settings
from backend.llm.base import BaseLLMOrchestrator

class OpenAIOrchestrator(BaseLLMOrchestrator):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini" # Using a fast default model

    async def audit_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=True,
            temperature=0.2
        )
        
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseLLMOrchestrator(ABC):
    @abstractmethod
    def audit_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        pass

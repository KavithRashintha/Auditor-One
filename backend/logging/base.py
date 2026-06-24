from abc import ABC, abstractmethod
from typing import Any

class ReasoningTraceRepository(ABC):
    @abstractmethod
    async def save(self, trace: dict[str, Any]) -> str:
        """
        Saves the reasoning trace and returns the path to the saved resource.
        """
        pass

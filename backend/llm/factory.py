from backend.config import settings
from backend.llm.base import BaseLLMOrchestrator
from backend.llm.openai_orchestrator import OpenAIOrchestrator
from backend.llm.anthropic_orchestrator import AnthropicOrchestrator

def get_llm_orchestrator() -> BaseLLMOrchestrator:
    if settings.LLM_PROVIDER.lower() == "anthropic":
        return AnthropicOrchestrator()
    return OpenAIOrchestrator()

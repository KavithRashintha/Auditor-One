from backend.config import settings
from backend.llm.base import BaseLLMOrchestrator
from backend.llm.openai_orchestrator import OpenAIOrchestrator
from backend.llm.anthropic_orchestrator import AnthropicOrchestrator
from backend.llm.hf_orchestrator import HFLLMOrchestrator

def get_llm_orchestrator() -> BaseLLMOrchestrator:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "anthropic":
        return AnthropicOrchestrator()
    elif provider == "hf":
        return HFLLMOrchestrator()
    return OpenAIOrchestrator()

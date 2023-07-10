from magic_assistant.config.global_config import GlobalConfig
from magic_assistant.models.llm.llm_factory import LlmFactory

GLOBAL_CONFIG = GlobalConfig()
LLM_FACTORY = LlmFactory()

def init_globals():
    GLOBAL_CONFIG.parse()
    LLM_FACTORY.init(GLOBAL_CONFIG.llm_config)

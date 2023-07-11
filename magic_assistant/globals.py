from loguru import logger

from magic_assistant.config.global_config import GlobalConfig
from magic_assistant.models.llm.llm_factory import LlmFactory

GLOBAL_CONFIG = GlobalConfig()
LLM_FACTORY = LlmFactory()

def init_globals():
    ret = GLOBAL_CONFIG.parse()
    if ret != 0:
        logger.error("init_globals failed")
        return -1

    ret = LLM_FACTORY.init(GLOBAL_CONFIG.llm_config)
    if ret != 0:
        logger.error("init_globals failed")
        return -1

    logger.debug("init_globals suc")
    return 0
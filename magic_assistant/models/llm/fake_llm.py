from loguru import logger

from magic_assistant.models.llm.base_llm import BaseLlm


class FakeLlm(BaseLlm):
    def predict(self, input: str):
        logger.debug("parse suc, output:%s" % input)
        return input
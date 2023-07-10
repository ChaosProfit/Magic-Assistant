from loguru import logger

from magic_assistant.models.llm.base_llm import BaseLlm
# from magic_assistant.models.llm.alpacca_lora.alpaca_lora import AlpacaLora
from magic_assistant.models.llm.fake_llm import FakeLlm
from magic_assistant.config.llm_config import LlmConfig

class LlmFactory(BaseLlm):
    _llm_model: BaseLlm = None

    def init(self, config: LlmConfig):
        self._llm_model: BaseLlm = None

        match config.model_type:
            case "fake":
                self._llm_model = FakeLlm()
            case _:
                logger.error("unsupported llm model type: %s" % config.model_type)

    def predict(self, input: str):
        self._llm_model.predict(input)

from loguru import logger

from magic_assistant.model.llm.base_llm import BaseLlm
# from magic_assistant.model.llm.alpacca_lora.alpaca_lora import AlpacaLora
from magic_assistant.model.llm.fake_llm import FakeLlm
from magic_assistant.model.llm.transformer_llm import TransformerLlm
from magic_assistant.model.llm.vicuna.vicuna import Vicuna
from magic_assistant.config.model_config import LlmConfig

class LlmFactory(BaseLlm):
    _llm_model: BaseLlm = None

    def init(self, config: LlmConfig) -> int:
        self._llm_model: BaseLlm = None

        match config.model_type:
            case "fake":
                self._llm_model = FakeLlm()
            case "transform_llm":
                self._llm_model = TransformerLlm(config.model_path)
            case "vicuna":
                self._llm_model = Vicuna(model_path=config.model_path)
            case _:
                logger.error("unsupported llm model type: %s" % config.model_type)
                return -1

        self._llm_model.init()

        return 0

    def run(self, input: str):
        return self._llm_model.run(input)

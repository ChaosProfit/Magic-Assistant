from loguru import logger

from magic_assistant.model.llm.base_llm import BaseLlm
from magic_assistant.model.llm.fake_llm import FakeLlm
from magic_assistant.model.llm.transformers_llm.transformers_llm import TransformersLlm
from magic_assistant.config.model_config import LlmConfig

class LlmFactory(BaseLlm):
    _llm_model: BaseLlm = None

    def init(self, config: LlmConfig) -> int:
        self._llm_model: BaseLlm = None

        match config.model_type:
            case "fake":
                self._llm_model = FakeLlm()
            case "transformers_llm":
                self._llm_model = TransformersLlm(model_path=config.model_path)
            case _:
                logger.error("unsupported llm model type: %s" % config.model_type)
                return -1

        self._llm_model.init()

        return 0

    def run(self, input: str):
        return self._llm_model.run(input)

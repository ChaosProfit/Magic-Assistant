from loguru import logger
from transformers import AutoTokenizer, AutoModel
from magic_assistant.model.llm.base_llm import BaseLlm

class TransformerLlm(BaseLlm):
    def __init__(self, model_path: str):
        self.model_path = model_path

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self._model = AutoModel.from_pretrained(self.model_path, trust_remote_code=True).half().cuda()

        self._model = self._model.eval()
        logger.debug("TransformersLlm init suc")

    def run(self, input: str):
        response, history = self._model.chat(self._tokenizer, input, history=[])
        logger.debug("infer suc, response:%s, history:%s" % (response, history))
        return response


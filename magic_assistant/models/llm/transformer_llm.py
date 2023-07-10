from loguru import logger
from transformers import AutoTokenizer, AutoModel
from magic_assistant.models.llm.base_llm import BaseLlm


class TransformerLlm(BaseLlm):
    def __init__(self, model_path: str):
        self._tokenizer: AutoTokenizer = None
        self._model: AutoModel = None

        self._tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self._model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()


    def predict(self, input: str):
        response, history = self._model.chat(self._tokenizer, input, history=[])
        logger.debug("infer suc, response:%s, history:%s" % (response, history))
        return response


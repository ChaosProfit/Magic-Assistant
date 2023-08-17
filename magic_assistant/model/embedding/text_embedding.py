from threading import Lock
from loguru import logger
import numpy as np
from sentence_transformers import SentenceTransformer, util
from magic_assistant.config.model_config import TextEmbeddingConfig
# from pydantic import BaseModel
from typing import Any

class TextEmbedding():
    _model: Any = None
    _get_lock: Lock = Lock()

    def init(self, config: TextEmbeddingConfig):
        self._model = SentenceTransformer(config.model_path)

        logger.debug("TextEmbedding init suc")
        return 0

    def get(self, text: str) -> list:
        try:
            self._get_lock.acquire()
            embedding = self._model.encode(text)
            vector = np.array(embedding)
            normalized_vector = vector / np.sqrt(np.sum(vector ** 2))

            return normalized_vector.tolist()
        finally:
            self._get_lock.release()

    def calculate_distance(self, vector1: list, vector2: list) -> float:
        cos_score = util.cos_sim(vector1, vector2)
        return cos_score
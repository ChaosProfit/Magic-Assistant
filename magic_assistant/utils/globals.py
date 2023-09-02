from typing import List
from loguru import logger

from magic_assistant.utils.tips import Tips
from magic_assistant.config.global_config import GlobalConfig
from magic_assistant.model.llm.llm_factory import LlmFactory
from magic_assistant.model.embedding.text_embedding import TextEmbedding
from magic_assistant.db.orm import Orm
from magic_assistant.vector.vector_db_factory import VectorDbFactory
from magic_assistant.oss.oss_factory import OssFactory


class Globals():
    def __init__(self):
        self.config: GlobalConfig = GlobalConfig()
        self.llm_factory: LlmFactory = LlmFactory()
        self.tips: Tips = Tips()
        self.text_embedding: TextEmbedding = TextEmbedding()
        self.vector_db_factory = VectorDbFactory()
        self.sql_orm: Orm = Orm()
        self.oss_factory: OssFactory = OssFactory()

    def init(self, init_models: List) -> int:
        ret = self.config.parse()
        if ret != 0:
            logger.error("init global config failed")
            return -1

        ret = self.tips.init(self.config.misc_config.language_code)
        if ret != 0:
            logger.error("init tips failed")
            return -1

        ret = self.oss_factory.init(self.config.oss_config)
        if ret != 0:
            logger.error("init oss failed")
            return -1

        if init_models == [] or "llm" in init_models:
            ret = self.llm_factory.init(self.config.model_config.llm)
            if ret != 0:
                logger.error("init llm factory failed")
                return -1

        if init_models == [] or "text_embedding" in init_models:
            ret = self.text_embedding.init(self.config.model_config.text_embedding)
            if ret != 0:
                logger.error("init text embedding failed")
                return -1

        ret = self.sql_orm.init(self.config.postgre_config.url)
        if ret != 0:
            logger.error("init orm failed")
            return -1

        ret = self.vector_db_factory.init(self.config.vector_db_config)
        if ret != 0:
            logger.error("init vector db failed")
            return -1

        return 0


GLOBALS = Globals()

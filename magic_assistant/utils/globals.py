from loguru import logger

from magic_assistant.utils.tips import Tips
from magic_assistant.config.global_config import GlobalConfig
from magic_assistant.model.llm.llm_factory import LlmFactory
from magic_assistant.model.embedding.text_embedding import TextEmbedding
from magic_assistant.db.orm import Orm
from magic_assistant.vector.vector_db_factory import VectorDbFactory


class Globals():
    def __init__(self):
        self.config: GlobalConfig = GlobalConfig()
        self.llm_factory: LlmFactory = LlmFactory()
        self.tips: Tips = Tips()
        self.text_embedding: TextEmbedding = TextEmbedding()
        self.vector_db_factory = VectorDbFactory()
        self.sql_orm: Orm = Orm()
        # self.sql_orm_base = declarative_base()

    def init(self) -> int:
        ret = self.config.parse()
        if ret != 0:
            logger.error("init global config failed")
            return -1

        ret = self.tips.init(self.config.misc_config.language_code)
        if ret != 0:
            logger.error("init tips failed")
            return -1

        ret = self.llm_factory.init(self.config.model_config.llm)
        if ret != 0:
            logger.error("init llm factory failed")
            return -1

        ret = self.sql_orm.init(self.config.postgre_config.url)
        if ret != 0:
            logger.error("init orm failed")
            return -1
        # self.sql_orm_base.metadata.create_all(self.sql_orm.engine)

        ret = self.vector_db_factory.init(self.config.vector_db_config)
        if ret != 0:
            logger.error("init vector db failed")
            return -1

        ret = self.text_embedding.init(self.config.model_config.text_embedding)
        if ret != 0:
            logger.error("init text embedding failed")
            return -1

        return 0

GLOBALS = Globals()

# SQL_ORM_BASE = declarative_base()
# GLOBAL_CONFIG = GlobalConfig()
# LLM_FACTORY = LlmFactory()
# TIPS: Tips = Tips()
# SQL_ORM = Orm()
# VECTOR_DB_FACTORY = VectorDbFactory()
# TEXT_EMBEDDING = TextEmbedding()

# def init_globals():
#     ret = GLOBAL_CONFIG.parse()
#     if ret != 0:
#         logger.error("init global config failed")
#         return -1
#
#     ret = TIPS.init(GLOBAL_CONFIG.misc_config.language_code)
#     if ret != 0:
#         logger.error("init tips failed")
#         return -1
#
#     ret = LLM_FACTORY.init(GLOBAL_CONFIG.model_config.llm)
#     if ret != 0:
#         logger.error("init llm factory failed")
#         return -1
#
#     ret = SQL_ORM.init(GLOBAL_CONFIG.postgre_config.url)
#     if ret != 0:
#         logger.error("init orm failed")
#         return -1
#     SQL_ORM_BASE.metadata.create_all(SQL_ORM.engine)
#
#     ret = VECTOR_DB_FACTORY.init(GLOBAL_CONFIG.vector_db_config)
#     if ret != 0:
#         logger.error("init vector db failed")
#         return -1
#
#     ret = TEXT_EMBEDDING.init(GLOBAL_CONFIG.model_config.text_embedding)
#     if ret != 0:
#         logger.error("init text embedding failed")
#         return -1
#
#     logger.debug("init_globals suc")
#     return 0

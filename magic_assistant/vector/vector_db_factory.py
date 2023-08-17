from loguru import logger
from typing import Dict, List
from threading import Lock

from magic_assistant.memory.memory_item import MemoryItem
# from magic_assistant.vector.vector import Vector
from magic_assistant.vector.base_vector_db import BaseVectorDb, FilterPara, OrderPara
from magic_assistant.vector.pgvector_adapter import PgVectorAdapter
from magic_assistant.config.vector_db_config import VectorDbConfig

class VectorDbFactory(BaseVectorDb):
    def __init__(self):
        self._vector_db: BaseVectorDb = None
        self._add_lock = Lock()
        self._search_lock = Lock()

    def init(self, config: VectorDbConfig) -> int:
        match config.db_type:
            case "pgvector":
                self._vector_db = PgVectorAdapter()
                self._vector_db.init(config.pg_vector)
            case _:
                logger.error("unsupported vector_db type:%s" % config.db_type)
                return -1

        return 0

    def add_memory(self, memory_item: MemoryItem):
        try:
            self._add_lock.acquire()
            self._vector_db.add_memory(memory_item)
        finally:
            self._add_lock.release()

    def search_memory(self, input_vector: list=[], filter_paras: List[FilterPara]=[], order_para: OrderPara=None, limit: int=5) -> List[MemoryItem]:
        try:
            self._search_lock.acquire()
            return self._vector_db.search_memory(input_vector, filter_paras, order_para, limit)
        finally:
            self._search_lock.release()

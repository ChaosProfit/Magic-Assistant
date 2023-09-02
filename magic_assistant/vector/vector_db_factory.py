from loguru import logger
from typing import Dict, List
from threading import Lock

from magic_assistant.memory.memory_item import VectorItem
# from magic_assistant.vector.vector import Vector
from magic_assistant.vector.base_vector_db import BaseVectorDb, FilterPara, OrderPara
from magic_assistant.vector.pgvector_adapter import PgVectorAdapter
from magic_assistant.config.vector_db_config import VectorDbConfig
from magic_assistant.vector.orm_vector import Vector
from magic_assistant.vector.milvus_adapter import MilvusAdapter


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
            case "milvus":
                self._vector_db = MilvusAdapter()
                self._vector_db.init(config.milvus)
            case _:
                logger.error("unsupported vector_db type:%s" % config.db_type)
                return -1

        return 0

    def add_memory(self, memory_item: VectorItem):
        try:
            self._add_lock.acquire()
            self._vector_db.add_memory(memory_item)
        finally:
            self._add_lock.release()

    def search_memory(self, input_vector: list=[], filter_paras: List[FilterPara]=[], order_para: OrderPara=None, limit: int=5) -> List[VectorItem]:
        try:
            self._search_lock.acquire()
            return self._vector_db.search_memory(input_vector, filter_paras, order_para, limit)
        finally:
            self._search_lock.release()

    def add_vector(self, vector: Vector):
        self._vector_db.add_vector(vector)

        # try:
        #     self._add_lock.acquire()
        #     self._vector_db.add_vector(vector)
        # finally:
        #     self._add_lock.release()

    def delete_vector(self, bucket_name: str, data_id: str):
        self._vector_db.delete_vector(bucket_name, data_id)

        # try:
        #     self._add_lock.acquire()
        #     self._vector_db.delete_vector(bucket_name, data_id)
        # finally:
        #     self._add_lock.release()

    def search_vector(self, input_vector: list=[], filter_paras: List[FilterPara]=[], order_para: OrderPara=None, limit: int=5) -> List[Vector]:
        return self._vector_db.search_vector(input_vector, filter_paras, order_para, limit)

        # try:
        #     self._search_lock.acquire()
        #     return self._vector_db.search_vector(input_vector, filter_paras, order_para, limit)
        # finally:
        #     self._search_lock.release()

    def add_finetune_data(self, finetune_data):
        return self._vector_db.add_finetune_data(finetune_data)

    def update_finetune_data(self, finetune_data):
        return self._vector_db.update_finetune_data(finetune_data)

    def get_finetune_data(self, hash: str):
        return self._vector_db.get_finetune_data(hash)
        # try:
        #     self._search_lock.acquire()
        #     return self._vector_db.get_finetune_data_item(hash)
        # finally:
        #     self._search_lock.release()

    def search_finetune_data(self, vector: List[float]=[], score: float=0.0, offset: int = 0, limit: int = 1):
        return self._vector_db.search_finetune_data(vector=vector, score=score, offset=offset, limit=limit)

        # try:
        #     self._search_lock.acquire()
        #     return self._vector_db.search_finetune_data_item(input_vector)
        # finally:
        #     self._search_lock.release()

    def is_finetune_data_existed(self, hash: str):
        return self._vector_db.is_finetune_data_existed(hash=hash)
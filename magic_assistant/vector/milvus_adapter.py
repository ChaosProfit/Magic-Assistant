from loguru import logger
from typing import List, Dict
from magic_assistant.config.milvus_config import MilvusConfig
from magic_assistant.vector.base_vector_db import OrderPara, FilterPara
from magic_assistant.memory.memory_item import VectorItem
from magic_assistant.vector.orm_vector import Vector
from magic_assistant.utils.utils import deep_dict_copy
from magic_assistant.finetune_llm.data_process.fintune_data import FinetuneData
from pymilvus import CollectionSchema, FieldSchema, DataType, Collection, connections, utility
from pymilvus.orm.search import Hit

DEFAULT_TEXT_VECTOR_LENGTH = 768



# class OrmMemory(Base):
#     __tablename__ = "memory"
#     id: str = Column(String, primary_key=True)
#     memory_type = Column(String)
#     agent_id = Column(String)
#     vector = mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
#     content = Column(String)
#     src_entity = Column(String)
#     target_entity = Column(String)
#     importance = Column(Integer)
#     timestamp = Column(BigInteger)
#
#     def __init__(self, memory: VectorItem):
#         for key, value in memory.__dict__.items():
#             self.__dict__[key] = value
#
#     def to_memory_item(self) -> VectorItem:
#         from magic_assistant.memory.memory_item import MEMORY_TYPE
#         memory_item: VectorItem = VectorItem(agent_id='', vector=[], content="", memory_type=MEMORY_TYPE.BLANK.value,
#                                              importance=1)
#         for key, value in self.__dict__.items():
#             memory_item.__dict__[key] = value
#
#         return memory_item

class MilvusMemory():
    def __init__(self):
        self.id: str = ""
        self.memory_type: str = ""
        self.agent_id: str = ""
        self.vector: List[float] = ""
        self.content: str = ""
        self.src_entity: str = ""
        self.target_entity: str = ""
        self.importance: int = 0
        self.timestamp: int = 0

    def get_schema(self):
        id = FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True)
        memory_type = FieldSchema(name="memory_type", dtype=DataType.VARCHAR, max_length=32)
        agent_id = FieldSchema(name="agent_id", dtype=DataType.VARCHAR, max_length=64)
        vector = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DEFAULT_TEXT_VECTOR_LENGTH)
        content = FieldSchema(name="output", dtype=DataType.VARCHAR, max_length=8192)
        src_entity = FieldSchema(name="src_entity", dtype=DataType.VARCHAR, max_length=64)
        target_entity = FieldSchema(name="target_entity", dtype=DataType.VARCHAR, max_length=64)
        importance = FieldSchema(name="importance", dtype=DataType.INT64)
        timestamp = FieldSchema(name="timestamp", dtype=DataType.INT64)

        schema = CollectionSchema(fields=[id, memory_type, agent_id, vector, content, src_entity, target_entity, importance, timestamp])
        return schema

    def to_milvus_data(self):
        return [
            [self.id],
            [self.memory_type],
            [self.agent_id],
            [self.vector],
            [self.content],
            [self.src_entity],
            [self.target_entity],
            [self.importance],
            [self.timestamp]
        ]
# class OrmVector(Base):
#     __tablename__ = "vectors"
#
#     id = Column(String, nullable=False)
#     user_id = Column(String, nullable=False, primary_key=True)
#     bucket_name = Column(String, nullable=False, primary_key=True)
#     hash = Column(String, primary_key=True)
#     data_id = Column(String, primary_key=True)
#     content = Column(String, nullable=False)
#     vector = mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
#     timestamp = Column(BigInteger, nullable=False)
#
#     def __init__(self, vector: VectorItem):
#         for key, value in vector.__dict__.items():
#             self.__dict__[key] = value
#
#     def to_memory_item(self) -> VectorItem:
#         from magic_assistant.memory.memory_item import MEMORY_TYPE
#         memory_item: VectorItem = VectorItem(agent_id='', vector=[], content="", memory_type=MEMORY_TYPE.BLANK.value,
#                                              importance=1)
#         for key, value in self.__dict__.items():
#             memory_item.__dict__[key] = value
#
#         return memory_item

# class OrmFinetuneData(Base):
#     __tablename__ = "finetune_data"
#
#     hash = Column(String, primary_key=True)
#     dataset_name = Column(String)
#     instruction: str = Column(String)
#     input = Column(String)
#     output = Column(String)
#     vector = mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
#     input_vector = mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
#     output_vector = mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
#     all_vector =  mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
#     timestamp = Column(BigInteger)
#     data_clean_type = Column(String)
#
#     def __init__(self, finetune_data: FinetuneData):
#         for key, value in finetune_data.__dict__.items():
#             self.__dict__[key] = value
#
#     def to_simple_json(self):
#         return {"instruction": self.instruction, "input": self.input, "output": self.output}

class MilvusVector():
    def __init__(self):
        self.id: str = ""
        self.user_id: str = ""
        self.bucket_name: str = ""
        self.hash: str = ""
        self.data_id: str = ""
        self.content: str = ""
        self.vector: List[float] = []
        self.timestamp: int = 0

        self.score = 0.0

    def get_schema(self):
        id = FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64)
        user_id = FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=64, is_primary=True)
        bucket_name = FieldSchema(name="bucket_name", dtype=DataType.VARCHAR, max_length=64, is_primary=True)
        hash = FieldSchema(name="input", dtype=DataType.VARCHAR, max_length=8192)
        data_id = FieldSchema(name="data_id", dtype=DataType.VARCHAR, max_length=64)
        content = FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8192)
        vector = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DEFAULT_TEXT_VECTOR_LENGTH)
        timestamp = FieldSchema(name="timestamp", dtype=DataType.INT64)

        schema = CollectionSchema(fields=[id, user_id, bucket_name, hash, data_id, content, vector, timestamp])
        return schema

    def from_vector(self, vector: Vector):
        deep_dict_copy(vector.__dict__, self.__dict__)

    def to_vector(self) -> Vector:
        vector: Vector = Vector()
        deep_dict_copy(self.__dict__, vector.__dict__)
        return vector

    def from_milvus_hit_dict(self, hit: Hit):
        for field in hit.entity.fields:
            self.__dict__[field] = hit.entity.get(field)
        self.score = hit.score

    def to_milvus_data(self) -> List:
        return [
            [self.id],
            [self.user_id],
            [self.bucket_name],
            [self.hash],
            [self.data_id],
            [self.content],
            [self.vector],
            [self.timestamp]
        ]

# from pydantic import BaseModel
# class MilvusDataItem(BaseModel):
#     name: str
#     value: str
#     type: str
#     length: str

class MilvusFinetuneData():
    def __init__(self):
        self.collection_name = "finetune_data"

        self.hash: str = ""
        self.dataset_name: str = ""
        self.instruction: str = ""
        self.input: str = ""
        self.output: str = ""
        self.vector: List[float] = ""
        self.timestamp: int = ""
        self.data_clean_type: str = ""

        self.score: float = 0.0

    def to_finetune_data(self) -> FinetuneData:
        finetune_data: FinetuneData = FinetuneData()
        deep_dict_copy(self.__dict__, finetune_data.__dict__)
        return finetune_data

    def from_finetune_data(self, finetune_data: FinetuneData):
        deep_dict_copy(finetune_data.__dict__, self.__dict__)

        for key, value in finetune_data.__dict__.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

    def from_milvus_hit_dict(self, hit: Hit):
        for field in hit.entity.fields:
            self.__dict__[field] = hit.entity.get(field)
        self.score = hit.score

    def get_schema(self):
        hash = FieldSchema(name="hash", dtype=DataType.VARCHAR, is_primary=True, max_length=64)
        dataset_name = FieldSchema(name="dataset_name", dtype=DataType.VARCHAR, max_length=64)
        instruction = FieldSchema(name="instruction", dtype=DataType.VARCHAR, max_length=8192)
        input = FieldSchema(name="input", dtype=DataType.VARCHAR, max_length=8192)
        output = FieldSchema(name="output", dtype=DataType.VARCHAR, max_length=8192)
        vector = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DEFAULT_TEXT_VECTOR_LENGTH)
        timestamp = FieldSchema(name="timestamp", dtype=DataType.INT64)
        data_clean_type = FieldSchema(name="data_clean_type", dtype=DataType.VARCHAR, max_length=32)

        schema = CollectionSchema(fields=[hash, dataset_name, instruction, input, output, vector,
                                          timestamp, data_clean_type])
        return schema

    def to_milvus_data(self) -> List:
        return [
            [self.hash],
            [self.dataset_name],
            [self.instruction],
            [self.input],
            [self.output],
            [self.vector],
            [self.timestamp],
            [self.data_clean_type]
        ]

    def to_simple_json(self):
        return {"instruction": self.instruction, "input": self.input, "output": self.output}

collection_name_list = ["finetune_data", "vector"]

class MilvusAdapter():
    def init(self, config: MilvusConfig):
        connections.connect(host=config.host, port=config.port)

        self.init_collection_index()

    def init_collection_index(self):
        for collection_name in collection_name_list:
            if utility.has_collection(collection_name) is False:
                milvus_fintune_data = MilvusFinetuneData()
                self.create_collection(collection_name, milvus_fintune_data.get_schema())
                self.create_index(collection_name=collection_name, field_name="vector", metric_type="COSINE", index_type="IVF_FLAT")

            collection = Collection(collection_name)
            collection.load(replica_number=1)

    def create_collection(self, collection_name: str, schema: CollectionSchema):
        from pymilvus import Collection

        collection = Collection(name=collection_name, schema=schema, using='default', shards_num=2)
        logger.debug("create_collection %s suc" % collection_name)
        # self._client.create_collection(collection_name=collection_name, fields=schema.to_dict())

    def create_index(self, collection_name: str, field_name: str, metric_type: str, index_type: str, params: Dict={"nlist": 1024}):
        index_params = {"metric_type": metric_type, "index_type": index_type, "params": params}
        collection = Collection(collection_name)
        collection.create_index(field_name=field_name, index_params=index_params)

        logger.debug("create_index suc, collection: %s, field_name: %s suc" % (collection_name, field_name))


    #     pass
    # def create_vector_extension(self) -> None:
    #     try:
    #         with Session(self._engine) as session:
    #             statement = text("CREATE EXTENSION IF NOT EXISTS vector")
    #             session.execute(statement)
    #             session.commit()
    #     except Exception as e:
    #         logger.exception(e)
    #
    # def create_tables(self):
    #     Base.metadata.create_all(self._engine)
    #
    # def add_memory(self, memory: VectorItem):
    #     orm_memory: OrmMemory = OrmMemory(memory)
    #     with Session(self._engine, expire_on_commit=False) as session:
    #         session.add(orm_memory)
    #         session.commit()
    #
    # def search_memory(self, input_vector: list = [], filter_paras: List[FilterPara] = [], order_para: OrderPara = None,
    #                   limit: int = 5) -> List[VectorItem]:
    #     memory_list: List[VectorItem] = []
    #     filter_str = self.filter_para_to_sql(filter_paras)
    #     vector_str = ""
    #     if input_vector != []:
    #         vector_str = "ORDER BY vector <-> '%s'" % input_vector
    #
    #     order_str = ""
    #     if order_para is not None:
    #         order_str = order_para.to_sql()
    #
    #     select_sql = "SELECT * FROM %s %s %s %s LIMIT %d" % \
    #                  (OrmMemory.__tablename__, filter_str, vector_str, order_str, limit)
    #     with Session(self._engine) as session:
    #         results: List[OrmMemory] = session.query(OrmMemory).from_statement(text(select_sql)).all()
    #         for orm_memory in results:
    #             memory_list.append(orm_memory.to_memory_item())
    #
    #     logger.debug("search_memory suc")
    #     return memory_list
    #
    # def filter_para_to_sql(self, filter_paras: List[FilterPara] = []) -> str:
    #     output_str = ""
    #     if len(filter_paras) == 0:
    #         logger.debug("filter_para_to_sql suc, filter_paras cnt is 0")
    #         return output_str
    #
    #     output_str += "WHERE "
    #     for filter_para in filter_paras:
    #         output_str += filter_para.to_sql() + " AND"
    #
    #     output_str = output_str.rstrip(" AND")
    #     logger.debug("filter_para_to_sql suc, filter_str:%s" % output_str)
    #     return output_str
    #
    def add_vector(self, vector: Vector) -> int:
        milvus_vector = MilvusVector()
        milvus_vector.from_vector(vector)

        return self.add_data(collection_name="vector", milvus_data=milvus_vector)

    def delete_vector(self, bucket_name: str, data_id: str) -> int:
        return self.delete_data(collection_name="vector", field_name="data_id", field_value=data_id)


    def search_vector(self, input_vector: list = [], filter_paras: List[FilterPara] = [], order_para: OrderPara = None,
                      limit: int = 5) -> List[Vector]:

        vector_list: List[Vector] = []
        hit_list: List = self.search_data(collection_name="vector", vector_field_name="vector", input_vector=input_vector, offset=0,
                                limit=limit, output_fields=['id', 'user_id', 'bucket_name', 'hash', 'data_id', 'content', 'timestamp'])
        for hit in hit_list:
            milvus_vector: MilvusVector = MilvusVector()
            milvus_vector.from_milvus_hit_dict(hit)
            vector_list.append(milvus_vector.to_vector())

        logger.debug("")
        return vector_list

    def add_finetune_data(self, finetune_data: FinetuneData) -> int:
        milvus_finetune_data = MilvusFinetuneData()
        milvus_finetune_data.from_finetune_data(finetune_data)
        return self.add_data("finetune_data", milvus_finetune_data.to_milvus_data())

    def get_finetune_data(self, hash: str) -> FinetuneData:
        finetune_data_dict = self.get_data(collection_name="finetune_data", field_name="hash", field_value=hash,
                             output_fields=["hash", "dataset_name", "instruction", "input", "output"])

        if len(finetune_data_dict) == 0:
            logger.debug("get_finetune_data failed")
            return None

        finetune_data = FinetuneData()
        deep_dict_copy(finetune_data_dict, finetune_data.__dict__)

        logger.debug("get_finetune_data suc")
        return finetune_data

    def search_finetune_data(self, vector: List[float]=[], score: float=0.0, offset: int = 0, limit: int = 1) -> List[FinetuneData]:
        milvus_finetune_data_list = []
        hit_list: List = self.search_data("finetune_data", "vector", vector, offset, limit,
                                output_fields=["hash", "dataset_name", "instruction", "input", "output"])

        for hit in hit_list:
            if hit.score < score:
                continue

            milvus_finetune_data: MilvusFinetuneData = MilvusFinetuneData()
            milvus_finetune_data.from_milvus_hit_dict(hit)
            milvus_finetune_data_list.append(milvus_finetune_data.to_finetune_data())

        logger.debug("search_finetune_data suc, result cnt:%d" % len(milvus_finetune_data_list))
        return milvus_finetune_data_list

    def is_finetune_data_existed(self, hash: str) -> bool:
        return self.is_data_existed("finetune_data", "hash", hash)

    def delete_data(self, collection_name: str, field_name: str, field_value: str) -> int:
        collection: Collection = Collection(collection_name)
        collection.delete(expr = "%s in ['%s']" % (field_name, field_value))

        logger.debug("delete_data suc")
        return 0

    def add_data(self, collection_name: str, milvus_data: List) -> int:
        collection: Collection = Collection(collection_name)
        collection.insert(milvus_data)

        logger.debug("add_data suc")
        return 0

    def is_data_existed(self, collection_name: str, field_name: str, field_value: str) -> bool:
        collection: Collection = Collection(collection_name)

        ret = collection.query(expr="%s in ['%s']" % (field_name, field_value))
        if len(ret) > 0:
            return True
        else:
            return False

    def get_data(self, collection_name: str, field_name: str, field_value: str, output_fields: List[str] = []) -> Dict:
        collection: Collection = Collection(collection_name)

        ret = collection.query(expr = "%s in ['%s']" % (field_name, field_value), output_fields=output_fields)
        if len(ret) > 0:
            return ret[0]
        else:
            return {}

    def search_data(self, collection_name: str, vector_field_name: str, input_vector: List[float]=[], offset: int = 0,
                    limit: int = 1, output_fields: List[str] = []) -> List:
        collection = Collection(collection_name)  # Get an existing collection.
        collection.load()
        search_params = {
            "metric_type": "COSINE",
            "offset": offset,
            "ignore_growing": False,
            "params": {"nprobe": 10}
        }

        results = collection.search(
            data=[input_vector],
            anns_field=vector_field_name,
            # the sum of `offset` in `param` and `limit`
            # should be less than 16384.
            param=search_params,
            limit=limit,
            expr=None,
            # set the names of the fields you want to
            # retrieve from the search result.
            output_fields=output_fields,
            consistency_level="Strong"
        )

        logger.debug("search suc, result cnt:%d" % len(results[0]._hits))
        return results[0]._hits

if __name__ == "__main__":
    milvus_config = MilvusConfig()
    milvus_config.port = "19530"
    milvus_config.host = "127.0.0.1"
    milvus_adapter = MilvusAdapter()
    milvus_adapter.init(milvus_config)

    milvus_fintune_data = MilvusFinetuneData()

    milvus_adapter.create_collection(milvus_fintune_data.collection_name, milvus_fintune_data.get_schema())
    pass
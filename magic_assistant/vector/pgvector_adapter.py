from loguru import logger
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from magic_assistant.config.postgre_config import PostgreConfig
from magic_assistant.vector.base_vector_db import OrderPara, FilterPara
from magic_assistant.memory.memory_item import VectorItem
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import Column, String, BigInteger, Integer, text
from sqlalchemy_utils import database_exists, create_database
from pgvector.sqlalchemy import Vector
from magic_assistant.finetune_llm.data_process.fintune_data import FinetuneData

Base = declarative_base()
DEFAULT_TEXT_VECTOR_LENGTH = 768



class OrmMemory(Base):
    __tablename__ = "memory"
    id: str = Column(String, primary_key=True)
    memory_type = Column(String)
    agent_id = Column(String)
    vector = mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
    content = Column(String)
    src_entity = Column(String)
    target_entity = Column(String)
    importance = Column(Integer)
    timestamp = Column(BigInteger)

    def __init__(self, memory: VectorItem):
        for key, value in memory.__dict__.items():
            self.__dict__[key] = value

    def to_memory_item(self) -> VectorItem:
        from magic_assistant.memory.memory_item import MEMORY_TYPE
        memory_item: VectorItem = VectorItem(agent_id='', vector=[], content="", memory_type=MEMORY_TYPE.BLANK.value,
                                             importance=1)
        for key, value in self.__dict__.items():
            memory_item.__dict__[key] = value

        return memory_item

class OrmVector(Base):
    __tablename__ = "vectors"

    id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    bucket_name = Column(String, nullable=False, primary_key=True)
    hash = Column(String, primary_key=True)
    data_id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    vector = mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
    timestamp = Column(BigInteger, nullable=False)

    def __init__(self, vector: VectorItem):
        for key, value in vector.__dict__.items():
            self.__dict__[key] = value

    def to_memory_item(self) -> VectorItem:
        from magic_assistant.memory.memory_item import MEMORY_TYPE
        memory_item: VectorItem = VectorItem(agent_id='', vector=[], content="", memory_type=MEMORY_TYPE.BLANK.value,
                                             importance=1)
        for key, value in self.__dict__.items():
            memory_item.__dict__[key] = value

        return memory_item

class OrmFinetuneData(Base):
    __tablename__ = "finetune_data"

    hash = Column(String, primary_key=True)
    dataset_name = Column(String)
    instruction: str = Column(String)
    input = Column(String)
    output = Column(String)
    vector = mapped_column(Vector(DEFAULT_TEXT_VECTOR_LENGTH))
    timestamp = Column(BigInteger)
    data_clean_type = Column(String)

    def __init__(self, finetune_data: FinetuneData):
        for key, value in finetune_data.__dict__.items():
            self.__dict__[key] = value

    def to_simple_json(self):
        return {"instruction": self.instruction, "input": self.input, "output": self.output}


class PgVectorAdapter():
    def __init__(self):
        self._param = None
        self._engine: Engine = None

    def init(self, config: PostgreConfig):
        if database_exists(config.url) is False:
            create_database(config.url)

        self._engine = create_engine(url=config.url)
        self.create_vector_extension()
        self.create_tables()

    def create_vector_extension(self) -> None:
        try:
            with Session(self._engine) as session:
                statement = text("CREATE EXTENSION IF NOT EXISTS vector")
                session.execute(statement)
                session.commit()
        except Exception as e:
            logger.exception(e)

    def create_tables(self):
        Base.metadata.create_all(self._engine)

    def add_memory(self, memory: VectorItem):
        orm_memory: OrmMemory = OrmMemory(memory)
        with Session(self._engine, expire_on_commit=False) as session:
            session.add(orm_memory)
            session.commit()

    def search_memory(self, input_vector: list = [], filter_paras: List[FilterPara] = [], order_para: OrderPara = None,
                      limit: int = 5) -> List[VectorItem]:
        memory_list: List[VectorItem] = []
        filter_str = self.filter_para_to_sql(filter_paras)
        vector_str = ""
        if input_vector != []:
            vector_str = "ORDER BY vector <-> '%s'" % input_vector

        order_str = ""
        if order_para is not None:
            order_str = order_para.to_sql()

        select_sql = "SELECT * FROM %s %s %s %s LIMIT %d" % \
                     (OrmMemory.__tablename__, filter_str, vector_str, order_str, limit)
        with Session(self._engine) as session:
            results: List[OrmMemory] = session.query(OrmMemory).from_statement(text(select_sql)).all()
            for orm_memory in results:
                memory_list.append(orm_memory.to_memory_item())

        logger.debug("search_memory suc")
        return memory_list

    def filter_para_to_sql(self, filter_paras: List[FilterPara] = []) -> str:
        output_str = ""
        if len(filter_paras) == 0:
            logger.debug("filter_para_to_sql suc, filter_paras cnt is 0")
            return output_str

        output_str += "WHERE "
        for filter_para in filter_paras:
            output_str += filter_para.to_sql() + " AND"

        output_str = output_str.rstrip(" AND")
        logger.debug("filter_para_to_sql suc, filter_str:%s" % output_str)
        return output_str

    def add_vector(self, vector: Vector) -> int:
        orm_vector: OrmVector = OrmVector(vector)
        with Session(self._engine, expire_on_commit=False) as session:
            session.add(orm_vector)
            session.commit()

    def delete_vector(self, bucket_name: str, data_id: str) -> int:
        with Session(self._engine, expire_on_commit=False) as session:
            session.query(OrmVector).filter(OrmVector.data_id == data_id).delete()
            session.commit()

    def search_vector(self, input_vector: list = [], filter_paras: List[FilterPara] = [], order_para: OrderPara = None,
                      limit: int = 5) -> List[OrmVector]:
        vector_list: List[VectorItem] = []
        filter_str = self.filter_para_to_sql(filter_paras)
        vector_str = ""
        if input_vector != []:
            vector_str = "ORDER BY vector <-> '%s'" % input_vector

        order_str = ""
        if order_para is not None:
            order_str = order_para.to_sql()

        select_sql = "SELECT * FROM %s %s %s %s LIMIT %d" % \
                     (OrmVector.__tablename__, filter_str, vector_str, order_str, limit)
        with Session(self._engine) as session:
            results: List[OrmVector] = session.query(OrmVector).from_statement(text(select_sql)).all()
            for orm_vector in results:
                vector_list.append(orm_vector.to_memory_item())

        logger.debug("search_vector suc")
        return vector_list

    def add_finetune_data(self, finetune_data: FinetuneData) -> int:
        orm_finetune_data = OrmFinetuneData(finetune_data)
        with Session(self._engine) as session:
            session.add(orm_finetune_data)
            session.commit()

        logger.debug("add_finetune_data suc")
        return 0

    def update_finetune_data(self, finetune_data: FinetuneData) -> int:
        orm_finetune_data = OrmFinetuneData(finetune_data)
        with Session(self._engine) as session:
            session.query(OrmFinetuneData).filter(OrmFinetuneData.hash == orm_finetune_data.hash).update({"language_code": orm_finetune_data.language_code})
            session.commit()

        logger.debug("add_finetune_data suc")
        return 0

    def get_finetune_data(self, hash: str) -> List[OrmFinetuneData]:
        with Session(self._engine) as session:
            finetune_data_list: List[OrmFinetuneData] = session.query(OrmFinetuneData).filter(OrmFinetuneData.hash == hash).all()

            finetune_data_list
            logger.debug("get_finetune_data suc, result cnt:%d" % len(finetune_data_list))
            return finetune_data_list

    def search_finetune_data(self, vector: List[float]=[], score: float=0.0, offset: int = 0, limit: int = 1) -> List[OrmFinetuneData]:
        score_str = ""
        vector_str = ""
        offset_str = ""

        if score > 0.0:
            score_str += "WHERE (1-(all_vector <=> '%s')) > %f" % (vector, score)

        if vector:
            vector_str = "ORDER BY all_vector <-> '%s'" % vector

        if offset > 0:
            offset_str = "OFFSET %d" % offset

        select_sql = "SELECT * FROM %s %s %s LIMIT %d" % \
                     (OrmFinetuneData.__tablename__, vector_str, offset_str, limit)

        with Session(self._engine) as session:
            finetune_data_list: List[OrmFinetuneData] = session.query(OrmFinetuneData).from_statement(text(select_sql)).all()
            return finetune_data_list

        logger.debug("search_finetune_data suc")
        return []


    def is_finetune_data_existed(self, hash: str) -> bool:
        with Session(self._engine) as session:
            finetune_data_list: List[OrmFinetuneData] = session.query(OrmFinetuneData).filter(OrmFinetuneData.hash == hash).all()
            if len(finetune_data_list) > 0:
                return True
            else:
                return False

    def test2(self, vector: List[float]=[], score: float=0.0, offset: int = 0, limit: int = 1) -> List[OrmFinetuneData]:
        score_filter_str = ""
        order_str = ""
        offset_str = ""

        # if score > 0.0:
        #     score_filter_str += "WHERE (1-(all_vector <=> '%s')) > %f" % (vector, score)

        if vector:
            order_str = "ORDER BY vector <-> '%s'" % vector

        if offset > 0:
            offset_str = "OFFSET %d" % offset

        select_sql = "SELECT * FROM %s %s %s %s LIMIT %d" % \
                     (OrmFinetuneData.__tablename__, score_filter_str, order_str, offset_str, limit)

        with Session(self._engine) as session:
            finetune_data_list: List[OrmFinetuneData] = session.query(OrmFinetuneData).from_statement(text(select_sql)).all()
            return finetune_data_list

        logger.debug("search_finetune_data suc")
        return []

    def test(self, vector: List[float]=[], score: float=0.0, offset: int = 0, limit: int = 1) -> List[OrmFinetuneData]:
        score_filter_str = ""
        order_str = ""
        offset_str = ""

        if score > 0.0:
            score_filter_str += "WHERE (1-(all_vector <=> '%s')) > %f" % (vector, score)

        if vector:
            order_str = "ORDER BY (1-(vector <=> '%s')) DESC" % vector

        if offset > 0:
            offset_str = "OFFSET %d" % offset

        select_sql = "SELECT * FROM %s %s %s %s LIMIT %d" % \
                     (OrmFinetuneData.__tablename__, score_filter_str, order_str, offset_str, limit)

        with Session(self._engine) as session:
            finetune_data_list: List[OrmFinetuneData] = session.query(OrmFinetuneData).from_statement(text(select_sql)).all()
            return finetune_data_list

        logger.debug("search_finetune_data suc")
        return []

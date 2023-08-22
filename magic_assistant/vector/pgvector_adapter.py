from loguru import logger
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from magic_assistant.config.postgre_config import PostgreConfig
from magic_assistant.vector.base_vector_db import OrderPara, FilterPara
from magic_assistant.memory.memory_item import MemoryItem
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import Column, String, BigInteger, Integer, text
from sqlalchemy_utils import database_exists, create_database
from pgvector.sqlalchemy import Vector

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

    def __init__(self, memory: MemoryItem):
        for key, value in memory.__dict__.items():
            self.__dict__[key] = value

    def to_memory_item(self) -> MemoryItem:
        from magic_assistant.memory.memory_item import MEMORY_TYPE
        memory_item: MemoryItem = MemoryItem(agent_id='', vector=[], content="", memory_type=MEMORY_TYPE.BLANK.value, importance=1)
        for key, value in self.__dict__.items():
            memory_item.__dict__[key] = value

        return memory_item

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

    def add_memory(self, memory: MemoryItem):
        orm_memory: OrmMemory = OrmMemory(memory)
        with Session(self._engine, expire_on_commit=False) as session:
            session.add(orm_memory)
            session.commit()


    def filter_para_to_sql(self, filter_paras: List[FilterPara]=[]) -> str:
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

    def search_memory(self, input_vector: list=[], filter_paras: List[FilterPara]=[], order_para: OrderPara=None, limit: int=5) -> List[MemoryItem]:
        memory_list: List[MemoryItem] = []
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

def test_add(pg_vector_adapter: PgVectorAdapter):
    memory: MemoryItem = MemoryItem(memory_type=MEMORY_TYPE.OBSERVATION.value, importance=1, agent_id="1", content="123", vector=[0.1, 0.2, 0.3])
    pg_vector_adapter.add_memory(memory)


def test_search(pg_vector_adapter: PgVectorAdapter):
    from magic_assistant.vector.base_vector_db import OPERATOR_TYPE, ORDER_TYPE
    filter_para = FilterPara(key="agent_id", operator=OPERATOR_TYPE.EQUAL, value='1')
    order_para = OrderPara(key="timestamp", type=ORDER_TYPE.ASC)

    pg_vector_adapter.search_memory(filter_paras=[filter_para], order_para=order_para)

if __name__ == "__main__":
    from magic_assistant.config.postgre_config import PostgreConfig
    from magic_assistant.memory.memory_item import MEMORY_TYPE

    postgre_config = PostgreConfig()
    postgre_config.url = "postgresql://writer:Abc123567.@127.0.0.1:5433/mojing"
    pg_vector = PgVectorAdapter()
    pg_vector.init(postgre_config)

    # test_add(pg_vector)
    test_search(pg_vector)
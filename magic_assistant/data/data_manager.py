from typing import List
from loguru import logger
from sqlalchemy.orm import Session

from magic_assistant.utils.globals import Globals
from magic_assistant.tools.doc_reader import DocReader
from magic_assistant.data.data import Data, DATA_TYPE


class DataManager():
    def __init__(self, globals: Globals):
        self.globals: Globals = globals
        self.doc_reader = DocReader()

    def add(self, data: Data) -> int:
        if data.type == DATA_TYPE.DOC.value:
            self.globals.oss_factory.add_file(data.id, data.file_bytes)
            data.content = self.doc_reader.process(data.name, data.file_bytes)

        data.split_content()
        for content in data.content_list:
            from magic_assistant.vector.orm_vector import Vector
            vector: Vector = Vector(data.user_id, data.bucket_name, data.id, data.content, [])
            vector.vector = self.globals.text_embedding.get(content)
            self.globals.vector_db_factory.add_vector(vector)

        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            session.add(data)
            session.commit()

        logger.debug("add suc")
        return 0

    def delete(self, data: Data) -> int:
        self.globals.vector_db_factory.delete_vector(data.bucket_name, data.id)

        with Session(self.globals.sql_orm.engine) as session:
            session.query(Data).filter(Data.id == data.id).delete()
            session.commit()

        logger.debug("delete suc")
        return 0

    def get(self) -> List[Data]:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            data_list: List[Data] = session.query(Data).filter().all()

        logger.debug("get suc, data_cnt:%d" % len(data_list))
        return data_list

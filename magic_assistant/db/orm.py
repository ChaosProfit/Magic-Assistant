from loguru import logger
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

BASE = declarative_base()

class Orm():
    def __init__(self):
        self.engine: Engine = None

    def init(self, url: str) -> int:
        if database_exists(url) is False:
            create_database(url)

        self.engine = create_engine(url=url)
        BASE.metadata.create_all(self.engine)

        logger.debug("init orm suc")
        return 0

from pydantic import BaseModel

from magic_assistant.config.postgre_config import PostgreConfig
from magic_assistant.config.milvus_config import MilvusConfig


class VectorDbConfig(BaseModel):
    db_type: str = ""
    pg_vector: PostgreConfig = PostgreConfig()
    milvus: MilvusConfig = MilvusConfig()

    def parse(self, vector_db_config_dict: dict):
        self.db_type = vector_db_config_dict["type"]
        if self.db_type == "pgvector":
            self.pg_vector.parse(vector_db_config_dict["pgvector"])
        elif self.db_type == "milvus":
            self.milvus.parse(vector_db_config_dict["milvus"])

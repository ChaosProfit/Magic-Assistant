from pydantic import BaseModel

from magic_assistant.config.postgre_config import PostgreConfig


class VectorDbConfig(BaseModel):
    db_type: str = ""
    pg_vector: PostgreConfig = PostgreConfig()

    def parse(self, vector_db_config_dict: dict):
        self.db_type = vector_db_config_dict["type"]
        if self.db_type == "pgvector":
            self.pg_vector.__dict__ = vector_db_config_dict["pgvector"]

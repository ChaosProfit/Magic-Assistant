from pydantic import BaseModel


class PostgreConfig(BaseModel):
    url: str = ""
    host: str = ""
    port: str = ""
    user: str = ""
    password: str = ""
    database: str = ""



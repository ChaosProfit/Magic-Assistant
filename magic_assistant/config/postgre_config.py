from magic_assistant.config.base_config import BaseConfig

class PostgreConfig(BaseConfig):
    url: str = ""
    host: str = ""
    port: str = ""
    user: str = ""
    password: str = ""
    database: str = ""



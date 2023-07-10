from pydantic import BaseModel


class MiscConfig(BaseModel):
    language_code: str = ""


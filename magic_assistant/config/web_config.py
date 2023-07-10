from pydantic import BaseModel

class WebConfig(BaseModel):
    port: str = ""

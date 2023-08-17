from pydantic import BaseModel

class WebConfig(BaseModel):
    port: int = 0

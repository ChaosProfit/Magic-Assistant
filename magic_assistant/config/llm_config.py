from pydantic import BaseModel

class LlmConfig(BaseModel):
    model_type: str = ""
    model_path: str = ""

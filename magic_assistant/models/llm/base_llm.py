from pydantic import BaseModel

class BaseLlm(BaseModel):
    def predict(self, input: str):
        raise NotImplementedError("this method should be implemented")
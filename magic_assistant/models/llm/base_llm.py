from pydantic import BaseModel

class BaseLlm(BaseModel):
    def init(self):
        raise NotImplementedError("this method should be implemented")

    def predict(self, input: str):
        raise NotImplementedError("this method should be implemented")
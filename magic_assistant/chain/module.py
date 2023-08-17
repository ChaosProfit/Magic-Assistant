from typing import Any
from pydantic import BaseModel

class Module(BaseModel):
    def init(self):
        raise NotImplementedError("should be implemented")

    def run(self, input: Any) -> (int, Any):
        raise NotImplementedError("should be implemented")

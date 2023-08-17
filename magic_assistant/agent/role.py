from pydantic import BaseModel
from typing import Dict


class Role(BaseModel):
    name: str
    intro: str = ""
    status: str = ""
    personality: str = ""
    age: float = 0
    init_memories: list = []

    def parse_dict(self, input_dict: Dict):
        for key, value in input_dict.items():
            if value is None:
                continue
            self.__dict__[key] = value

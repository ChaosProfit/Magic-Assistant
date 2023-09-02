from typing import List
from pydantic import BaseModel
import time
from enum import Enum

class DATA_CLEAN_TYPE(Enum):
    CLEAN = "clean"
    OUTPUT_SHORT = "output_short"


class FinetuneData(BaseModel):
    hash: str = ""
    dataset_name: str = ""
    instruction: str = ""
    input: str = ""
    output: str = ""
    vector: List[float] = []
    timestamp: int = int(time.time()*1000)
    data_clean_type: str = ""

    score: float = 0.0

    def to_simple_json(self):
        return {"instruction": self.instruction, "input": self.input, "output": self.output}
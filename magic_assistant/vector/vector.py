import time
import uuid

from typing import List
class Vector():
    def __init__(self, agent_id: str, vector: List[float], content: str):
        self.agent_id: str = agent_id
        self.vector: List[float] = vector
        self.content: str = content
        self.id: str = uuid.uuid1().hex
        self.timestamp: int = int(time.time()*1000)


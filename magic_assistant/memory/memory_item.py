from enum import Enum
from magic_assistant.vector.vector import Vector
from typing import List

class MEMORY_TYPE(Enum):
    BLANK = "blank"
    OBSERVATION = "observation"
    PLAN = "plan"
    REFLECTION = "reflection"
    MEMORY = "memory"


class MemoryItem(Vector):
    def __init__(self, agent_id: str, vector: List[float], content: str, memory_type: str=MEMORY_TYPE.OBSERVATION.value,
                 importance: int=0, src_entity: str="", relation: str="", target_entity: str=""):
        if len(src_entity) > 0 and len(relation) > 0 and len(target_entity) > 0:
            content = "%s %s %s: %s" % (src_entity, relation, target_entity, content)

        super(MemoryItem, self).__init__(agent_id=agent_id, vector=vector, content=content)
        self.memory_type: str = memory_type
        self.importance: int = importance
        self.weight: float = 0
        self.src_entity: str = src_entity
        self.relation: str = relation
        self.target_entity: str = target_entity

    def to_str(self):
        if len(self.src_entity) == 0 and len(self.relation) == 0 and len(self.target_entity) == 0:
            return self.content
        else:
            return "%s %s %s: %s" % (self.src_entity, self.relation, self.target_entity, self.content)

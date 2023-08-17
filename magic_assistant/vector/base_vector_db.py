from enum import Enum
from pydantic import BaseModel
from typing import List
from typing import Dict
from magic_assistant.vector.vector import Vector
from magic_assistant.memory.memory_item import MemoryItem


class OPERATOR_TYPE(Enum):
    EQUAL = "="
    GREATER = ">"
    SMALLER = "<"
    IN = "in"

class ORDER_TYPE(Enum):
    DESC = "desc"
    ASC = "asc"

class OrderPara(BaseModel):
    key: str
    type: ORDER_TYPE

    def to_sql(self) -> str:
        output_str = "ORDER BY %s %s" % (self.key, self.type.value)
        return output_str

    # def to_orm(self) -> str:
    #     return 'sqlalchemy.%s("%s")' % (self.type.value, self.key)

class FilterPara(BaseModel):
    key: str
    operator: OPERATOR_TYPE
    value: str

    def to_sql(self) -> str:
        output_str = ""
        if self.operator in [OPERATOR_TYPE.EQUAL, OPERATOR_TYPE.GREATER, OPERATOR_TYPE.SMALLER]:
            if isinstance(self.value, str):
                output_str = "%s %s '%s'" % (self.key, self.operator.value, self.value)
            else:
                output_str = "%s %s %s" % (self.key, self.operator.value, self.value)
        elif self.operator == OPERATOR_TYPE.IN:
            output_str = "'%s' %s [%s]" % (self.key, self.operator.value, self.value)

        return output_str

    # def to_orm(self) -> str:
    #     if isinstance(self.value, str):
    #         output_str = "%s%s'%s'" % (self.key, self.operator.value, self.value)
    #     else:
    #         output_str = "%s%s%s" % (self.key, self.operator.value, self.value)
    #
    #     return output_str

class BaseVectorDb:
    def init(self):
        raise NotImplementedError("Should be implemented")

    def add_mmeory(self, memory: MemoryItem):
        raise NotImplementedError("Should be implemented")

    def search_memory(self, input_vector: list=[], filter_paras: List[FilterPara]=[], order_para: OrderPara=None, limit: int=5) -> List[MemoryItem]:
        raise NotImplementedError("Should be implemented")

    def filter_para_to_sql(self, filter_paras: list[FilterPara]) -> str:
        output_str = ""
        if len(filter_paras) == 0:
            return output_str

        output_str += "WHERE "

        for filter_para in filter_paras:
            output_str += filter_para.to_sql() + " AND"

        output_str = output_str.rstrip(" AND")
        return output_str
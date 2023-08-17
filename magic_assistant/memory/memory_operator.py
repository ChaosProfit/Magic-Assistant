import time
from loguru import logger
from typing import List, Dict, Callable
from magic_assistant.memory.memory_item import MemoryItem
from magic_assistant.vector.base_vector_db import OrderPara, ORDER_TYPE, FilterPara, OPERATOR_TYPE
from magic_assistant.utils.globals import Globals
from magic_assistant.memory.memory_item import MEMORY_TYPE
from magic_assistant.utils.utils import base_decode_llm_output

TIME_DECAY_FACTOR = 0.99
MEMORY_TOKEN_SIZE = 1024

class MemoryOperator():
    def __init__(self, agent_id: str, globals: Globals, timestamp_callack: Callable):
        self.agent_id: str = agent_id
        self.globals: Globals = globals
        self.timestamp_callback: Callable = timestamp_callack
        self.unprocessed_observations: List[MemoryItem] = []

    def add_memory_item(self, content: str, memory_type: MEMORY_TYPE=MEMORY_TYPE.OBSERVATION, src_entity: str="", relation: str="", target_entity: str="") -> int:
        vector = self.globals.text_embedding.get(content)
        memory_item: MemoryItem = MemoryItem(agent_id=self.agent_id, content=content, memory_type=memory_type.value,
                                             vector=vector, src_entity=src_entity, relation=relation, target_entity=target_entity)
        memory_item.importance = self._get_memory_importance(content)
        self.globals.vector_db_factory.add_memory(memory_item)
        if memory_item.memory_type == MEMORY_TYPE.OBSERVATION.value:
            self.unprocessed_observations.append(memory_item)

        logger.debug("add_memory_item suc")

    def from_list(self, input_list: List[Dict]):
        input_list.reverse()
        for item in input_list:
            memory_item: MemoryItem = MemoryItem(agent_id=self.agent_id, vector=self.globals.text_embedding.get(item["content"]),
                                                 content=item["content"], memory_type=item["memory_type"])
            if memory_item.memory_type == MEMORY_TYPE.OBSERVATION.value:
                self.unprocessed_observations.append(memory_item)

        logger.debug("from_list suc")

    def get_summarized_memory_str(self, observation: MemoryItem) -> str:
        context_vector = self.globals.text_embedding.get(observation.content)
        memory_list: List[MemoryItem] = self._load_memory_by_relevant(context_vector)
        summarized_memory_str: str = self._summary_memory_to_str_v1(memory_list, observation.content)

        logger.debug("get_summarized_memory_str suc, context:%s, summarized_str:%s" % (observation.content, summarized_memory_str))
        return summarized_memory_str

    def _get_memory_importance(self, content: str) -> int:
        return 5
        prompt_template = \
'''
Memory: {memory}
Evaluate the memory between 1 to 10. 1 is usual and 10 is very important. Output in the next given format.
<Score>$SCORE</Score>
<Explanation>$EXPLANATION</Explanation>
'''

        prompt = prompt_template.format(memory=content)
        llm_output = self.globals.llm_factory.run(prompt)
        score_str = base_decode_llm_output(llm_output=llm_output, key="Score")
        try:
            score = int(score_str)
        except Exception as e:
            logger.error("catch exception:%s, score:%s" % (str(e), score))
            score = 5

        logger.debug("_get_memory_weight suc, memory:%s, importance:%s" % (content, score))
        return int(score)

    def _summary_memory_to_str_v1(self, memory_list: List[MemoryItem], context: str) -> str:
        summarized_memory_l1 = ""
        for memory in memory_list:
            if len(summarized_memory_l1) + len(memory.content) < MEMORY_TOKEN_SIZE:
                summarized_memory_l1 += memory.content + "\n"

            if len(summarized_memory_l1) >= MEMORY_TOKEN_SIZE:
                break

        prompt_template = \
'''
Memories:
{memories}

Context:
{context}

According to the context, summarize the memories. The summarized memory is smaller than {memory_token_length}. Output in
the next given format.
<SummarizedMemory>$SUMMARIZED_MEMORY</SummarizedMemory>
<Explanation>$EXPLANATION</Explanation>
'''
        prompt = prompt_template.format(memories=summarized_memory_l1, context=context, memory_token_length=MEMORY_TOKEN_SIZE)
        llm_output = self.globals.llm_factory.run(prompt)
        summarized_memory_l2 = base_decode_llm_output(llm_output, "SummarizedMemory")

        logger.debug("_summary_memory_to_str_v1 suc")
        return summarized_memory_l2

    def _get_memory(self, context_vector: List[float]) -> list[MemoryItem]:
        id_2_memory_dict = {}
        id_2_memory_weigh_dict = {}

        time_memories = self._load_memory_by_time()
        importance_memories = self._load_memory_by_importance()
        if len(context_vector) == 0:
            relevant_memories = []
        else:
            relevant_memories = self._load_memory_by_relevant(context_vector)

        for memory in time_memories:
            if memory.id not in id_2_memory_dict:
                id_2_memory_dict[memory.id] = memory
                id_2_memory_weigh_dict[memory.id] = memory.weight
        for memory in relevant_memories:
            if memory.id not in id_2_memory_dict:
                id_2_memory_dict[memory.id] = memory
                id_2_memory_weigh_dict[memory.id] = memory.weight
        for memory in importance_memories:
            if memory.id not in id_2_memory_dict:
                id_2_memory_dict[memory.id] = memory
                id_2_memory_weigh_dict[memory.id] = memory.weight

        memory_id_weight_tuple_list = sorted(id_2_memory_weigh_dict.items(), key=lambda x: x[1])
        memory_list = []
        for memory_id_weight_tuple in memory_id_weight_tuple_list:
            memory_id = memory_id_weight_tuple[0]
            memory = id_2_memory_dict[memory_id]
            memory_list.append(memory)

        logger.debug("_get_memory_v1 suc, memory_cnt: %d" % len(memory_list))
        return memory_list

    def _calculate_memory_weight(self, memory: MemoryItem, context_vector: List[float]) -> float:

        hours = int((self._get_timestamp() - memory.timestamp) / 1000 / 3600)
        time_weight = TIME_DECAY_FACTOR**hours

        importance_weight = memory.importance/10
        relevant_weight = self.globals.text_embedding.calculate_distance(memory.vector, context_vector)

        memory_weight = time_weight + importance_weight + relevant_weight

        logger.debug("_calculate_memory_weight suc, memory_id:%s, weight:%f" % (memory.id, memory_weight))
        return memory_weight

    def _get_timestamp(self) -> int:
        if self.timestamp_callback is None:
            return int(time.time()*1000)
        else:
            return self.timestamp_callback()

    def _load_memory_by_time(self, limit=10, memory_type: MEMORY_TYPE=MEMORY_TYPE.BLANK) -> list[MemoryItem]:
        order_para: OrderPara = OrderPara(key="timestamp", type=ORDER_TYPE.DESC)
        filter_paras = []
        filter_paras.append(FilterPara(key="agent_id", operator=OPERATOR_TYPE.EQUAL, value=self.agent_id))
        if memory_type != MEMORY_TYPE.BLANK:
            filter_paras.append(FilterPara(key="memory_type", operator=OPERATOR_TYPE.EQUAL, value=memory_type.value))

        memories = self.globals.vector_db_factory.search_memory(filter_paras=filter_paras, order_para=order_para, limit=limit)

        logger.debug("_load_memory_by_time suc, memories cnt: %d" % len(memories))
        return memories

    def _load_memory_by_importance(self) -> List[MemoryItem]:
        order_para: OrderPara = OrderPara(key="importance", type=ORDER_TYPE.DESC)

        filter_paras = []
        filter_paras.append(FilterPara(key="agent_id", operator=OPERATOR_TYPE.EQUAL, value=self.agent_id))

        memories = self.globals.vector_db_factory.search_memory(filter_paras=filter_paras, order_para=order_para, limit=10)

        logger.debug("_load_memory_by_importance suc, memories cnt: %d" % len(memories))
        return memories

    def _load_memory_by_relevant(self, context_vector: List) -> list[MemoryItem]:
        memories = self.globals.vector_db_factory.search_memory(input_vector=context_vector, limit=10)
        return memories

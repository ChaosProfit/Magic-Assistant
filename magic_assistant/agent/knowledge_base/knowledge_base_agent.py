from loguru import logger

from magic_assistant.agent.base_agent import BaseAgent
from magic_assistant.memory.simeple_memory import SimpleMemory
from magic_assistant.message import Message
from magic_assistant.agent.knowledge_base.prompt import build_prompt, decode_llm_output

class KnowledgeBaseAgent(BaseAgent):
    # _memory: SimpleMemory = None

    def init(self):
        pass
        # self._memory: SimpleMemory = SimpleMemory(agent_id=self.agent_id, orm_engine=self.orm_engine, memory_size=self.agent_config.memory_size)
        # self._memory.load()

    def process(self, person_input: str) -> str:
        message: Message = Message(self.agent_id)
        if message.person_input.strip(" ") == "":
            return ""

        person_input_embedding = self.globals.text_embedding.get(message.person_input)

        from typing import List
        from magic_assistant.vector.orm_vector import Vector
        from magic_assistant.vector.base_vector_db import FilterPara, OPERATOR_TYPE

        user_id_filter: FilterPara = FilterPara(key="user_id", operator=OPERATOR_TYPE.EQUAL, value="")
        bucket_name_filter: FilterPara = FilterPara(key="bucket_name", operator=OPERATOR_TYPE.EQUAL, value="")
        filter_para_list: List[FilterPara] = [user_id_filter, bucket_name_filter]
        vector_list: [Vector] = self.globals.vector_db_factory.search_vector(person_input_embedding, filter_paras=filter_para_list)

        context = ""
        for vector in vector_list:
            context += vector.content + "\n"

        prompt = build_prompt(user_object=message.person_input, context=context)

        llm_output = self.llm_factory.run(prompt)
        message.assistant_output = decode_llm_output(llm_output)

        return message.assistant_output
import time
import uuid
from typing import Callable, List
from loguru import logger
from magic_assistant.memory.memory_item import MemoryItem
from magic_assistant.memory.memory_operator import MemoryOperator
from magic_assistant.utils.globals import Globals
from magic_assistant.agent.role_play.prompt import build_communicate_prompt, decode_communicate_output_batch, build_respond_prompt, decode_respond_output
from magic_assistant.agent.role_play.agent_react import AgentReact
from typing import Dict, Any
from magic_assistant.io.base_io import BaseIo

from magic_assistant.db.orm import BASE
from sqlalchemy import Column, String


class AgentMeta(BASE):
    __tablename__ = "agent"

    id = Column(String, primary_key=True)
    name = Column(String)
    sandbox_id = Column(String)
    intro = Column(String)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.name = ""
        self.sandbox_id = ""
        self.intro = ""


class RolePlayAgent():
    def __init__(self, agent_meta: AgentMeta, globals: Globals, io: BaseIo,
                 timestamp_callback: Callable):
        self.agent_config = globals.config.agent_config
        self.globals: Globals = globals
        self.io: BaseIo = io

        self.timestamp_callback: Callable = timestamp_callback
        self.meta: AgentMeta = agent_meta
        self.memory_operator: MemoryOperator = MemoryOperator(agent_id=self.meta.id, globals=globals,
                                                              timestamp_callack=self.timestamp_callback)

    def process(self, agents_in_context: List[str]) -> List[AgentReact]:
        agent_react_list = []
        if len(self.memory_operator.unprocessed_observations) == 0:
            logger.error("The agent:%s return None action." % self.meta.name)
            return agent_react_list

        while len(self.memory_operator.unprocessed_observations) > 0:
            observation = self.memory_operator.unprocessed_observations.pop()
            sub_agent_react_list = self._process(observation, agents_in_context)
            agent_react_list += sub_agent_react_list

        logger.debug("process")
        return agent_react_list

    def _process(self, observation: MemoryItem, agents_in_context: List[str]) -> List[AgentReact]:
        agents_in_context_str = self._list_to_str(agents_in_context)
        react_type = self._decide_next_react_type(observation, agents_in_context_str)
        if react_type == "communicate":
            return self._communicate(observation, agents_in_context_str)
        elif react_type == "respond":
            return self._respond(observation)
        else:
            logger.error("unsupported react_type:%s" % react_type)
            return []

    def get_time_format_str(self) -> str:
        return time.asctime(time.localtime(self.timestamp_callback() / 1000))

    def _parse_dict(self, input_dict: Dict[str, Any]):
        for key, value in input_dict.items():
            if value is None:
                continue
            elif key == "memories":
                for memory in value:
                    self.memory_operator.add_memory_item(content=memory)
                pass
            else:
                self.meta.__dict__[key] = value

    def _list_to_str(self, input_list: list) -> str:
        output_str = ""
        for item in input_list:
            if item == self.meta.name:
                continue

            output_str += item + ", "

        return output_str.rstrip(", ")

    def _decide_next_react_type(self, observation: MemoryItem, agents_in_context_str: str) -> str:
        from magic_assistant.agent.role_play.prompt import build_decide_next_react_type_prompt, decode_decide_next_react_type_output
        prompt = build_decide_next_react_type_prompt(agent_name=self.meta.name, intro=self.meta.intro,
                                                     summarized_memory=self.memory_operator.get_summarized_memory_str(observation),
                                                     observation=observation.content, agents_in_context=agents_in_context_str)

        llm_output = self.globals.llm_factory.run(prompt)

        react_type = decode_decide_next_react_type_output(llm_output)
        if self.agent_config.output_intermediate_steps:
            self.io.output("agent %s decided to: %s" % (self.meta.name, react_type))

        logger.debug("_decide_next_react_type, react_type:%s" % (react_type))
        return react_type

    def _respond(self, observation: MemoryItem) -> List[AgentReact]:
        respond_to_agent = observation.src_entity
        prompt = build_respond_prompt(agent_name=self.meta.name, intro=self.meta.intro,
                                      summarized_memory=self.memory_operator.get_summarized_memory_str(observation),
                                      observation=observation.content, respond_to=respond_to_agent)

        llm_output = self.globals.llm_factory.run(prompt)

        agent_react: AgentReact = decode_respond_output(llm_output, self.meta.name, respond_to_agent)
        if self.agent_config.output_intermediate_steps:
            self.io.output("agent %s respond to %s: %s" % (agent_react.src_entity, agent_react.target_entity, agent_react.react_content))

        logger.debug("_respond suc, agent_react:%s" % (agent_react.__dict__))
        return [agent_react]

    def _communicate(self, observation: MemoryItem, agents_in_context_str: str) -> List[AgentReact]:
        prompt = build_communicate_prompt(agent_name=self.meta.name, intro=self.meta.intro,
                                          summarized_memory=self.memory_operator.get_summarized_memory_str(observation),
                                          observation=observation.content, agents_in_context=agents_in_context_str)

        llm_output = self.globals.llm_factory.run(prompt)

        agent_react_list: List[AgentReact] = decode_communicate_output_batch(llm_output, self.meta.name)
        if self.agent_config.output_intermediate_steps:
            for agent_react in agent_react_list:
                self.io.output("agent %s said to %s: %s" % (agent_react.src_entity, agent_react.target_entity, agent_react.react_content))

        # for agent_react in agent_react_list:
        #     print("_communicate suc, agent_react:%s" %
        #              (agent_react.__dict__))
        return agent_react_list

    def _do_something(self):
        pass
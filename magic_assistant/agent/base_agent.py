import json
import uuid
from sqlalchemy import Column, String, BigInteger
from loguru import logger
from enum import Enum
import time

from typing import Dict
from magic_assistant.config.agent_config import AgentConfig
from magic_assistant.utils.globals import Globals
from magic_assistant.io.base_io import BaseIo
from magic_assistant.db.orm import BASE


class AGENT_TYPE(Enum):
    PLAN = "plan"
    ROLE_PLAY = "role_play"
    EXECUTE_CMD = "execute_cmd"
    CHAT = "chat"
    KNOWLEDGE_BASE = "knowledge_base"

class AgentMeta(BASE):
    __tablename__ = "agent"
    user_id = Column(String, primary_key=True, nullable=False)
    name = Column(String, primary_key=True, nullable=False)
    id = Column(String, nullable=False)
    sandbox_id = Column(String)
    intro = Column(String)
    type = Column(String, nullable=False)
    create_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.name = ""
        self.user_id = "default"
        self.sandbox_id = ""
        self.intro = ""
        self.type = ""
        self.create_timestamp = int(time.time() * 1000)

    def from_str(self, input_str: str) -> int:
        if input_str is None:
            return -1

        input_dict = json.loads(input_str)
        self.from_dict(input_dict)
        return 0

    def from_dict(self, input_dict: Dict) -> int:
        for key, value in input_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] =  value

        if self.name == "" or self.type == "":
            logger.error("from_dict failed, lack basic info, dict:%s" % input_dict)
            return -1

        if self.type not in [item.value for item in AGENT_TYPE]:
            logger.error("unsupported agent_type:%s" % self.type)
            return -1

        logger.debug("from_dict suc")
        return 0

    def to_dict(self) -> Dict:
        output_dict = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            output_dict[key] = value

        return output_dict

class BaseAgent():
    def __init__(self, agent_meta: AgentMeta, globals: Globals, io: BaseIo):
        self.agent_config: AgentConfig = globals.config.agent_config
        self.agent_meta: AgentMeta = agent_meta
        self.globals: Globals = globals
        self.io: BaseIo = io

    agent_id: str = "default"
    current_loop_count: int = 0

    def init(self):
        raise NotImplementedError("Should be implemented")

    def run(self):
        raise NotImplementedError("Should be implemented")

    def process(self, person_input: str):
        raise NotImplementedError("Should be implemented")

    def output_intermediate_steps(self, output: str):
        if self.agent_config.output_intermediate_steps:
            self.io.output(output)


if __name__ == "__main__":
    AGENT_TYPE.to_list()
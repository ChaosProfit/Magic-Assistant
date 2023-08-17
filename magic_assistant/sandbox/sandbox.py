from loguru import logger
import uuid
from sqlalchemy import Column, String, BigInteger
import os.path
import time
from typing import Dict, List


from magic_assistant.agent.role_play.role_play_agent import RolePlayAgent
from magic_assistant.agent.role_play.agent_react import AgentReact
from magic_assistant.agent.agent_manager import AgentManager
from magic_assistant.utils.globals import Globals
from magic_assistant.io.base_io import BaseIo
from magic_assistant.db.orm import BASE

class SandboxMeta(BASE):
    __tablename__ = "sandbox"
    id = Column(String, primary_key=True)
    name = Column(String)
    user_id = Column(String)
    sandbox_timestamp = Column(BigInteger)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.user_id = "default"
        self.sandbox_timestamp = int(time.time() * 1000)

class Sandbox():
    def __init__(self, sandbox_meta: SandboxMeta, role_play_config_path: str, globals: Globals, io: BaseIo):
        self.meta = sandbox_meta
        self.role_play_config_path: str = role_play_config_path
        self.globals: Globals = globals
        self.io: BaseIo = io
        self.time_interval_per_loop: int = 60000
        self.agent_manager = AgentManager(globals=globals)
        self.agents: Dict[str, RolePlayAgent] = {}
        self.agent_names: List[str] = []
        self.__post_init__()

    def __post_init__(self):
        agent_config_path = os.path.join(self.role_play_config_path, "agent.yml")
        self.agents = self.agent_manager.get_or_create_batch(agent_config_path, self.io, self.get_sandbox_timestamp, self.meta.id)
        for _, agent in self.agents.items():
            self.agent_names.append(agent.meta.name)

    def start_loop(self):
        while True:
            for _, agent in self.agents.items():
                agent_react_list: List[AgentReact] = agent.process(agents_in_context=self.agent_names)
                if agent_react_list is None or len(agent_react_list) == 0:
                    logger.error("agent %s process react is None" % agent.meta.name)
                    continue

                for agent_react in agent_react_list:
                    if (agent_react.react_type == "communicate" or agent_react.react_type == "respond") and agent_react.target_entity in self.agents:
                        target_agent: RolePlayAgent = self.agents[agent_react.target_entity]
                        target_agent.memory_operator.add_memory_item(content=agent_react.react_content, src_entity=agent.meta.name, relation="said to", target_entity=target_agent.meta.name)
                    else:
                        logger.error("react processed failed, react:%s, agents:%s" % (agent_react.__dict__, self.agents))

            self.meta.sandbox_timestamp += self.time_interval_per_loop
            time.sleep(3)

    def get_sandbox_timestamp(self) -> int:
        return self.meta.sandbox_timestamp

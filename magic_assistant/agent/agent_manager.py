from loguru import logger
from typing import List, Any, Dict, Callable
from sqlalchemy.orm import Session
from magic_assistant.agent.role_play.role_play_agent import RolePlayAgent, AgentMeta
from magic_assistant.utils.globals import Globals
from magic_assistant.config.utils import get_yaml_content
from magic_assistant.io.base_io import BaseIo


class AgentManager():

    def __init__(self, globals: Globals):
        self.globals: Globals = globals

    def create_batch(self, config_path: str, io: BaseIo, timestamp_callback: Callable) -> Dict[str, RolePlayAgent]:
        agent_dicts: [str, RolePlayAgent] = {}
        yaml_content = get_yaml_content(config_path)
        for _, agent_meta_dict in yaml_content.items():
            agent = self.create(agent_meta_dict, io, timestamp_callback)
            agent_dicts[agent.meta.name] = agent

        logger.debug("create_batch suc, agents cnt:%d" % len(agent_dicts))
        return agent_dicts

    def create(self, yaml_content: Dict[str, Any], io: BaseIo, timestamp_callback: Callable) -> RolePlayAgent:
        agent_meta: AgentMeta = AgentMeta()
        for key, value in yaml_content.items():
            if key == "memories" or value is None:
                continue

            agent_meta.__dict__[key] = value

        agent: RolePlayAgent = RolePlayAgent(agent_meta=agent_meta, globals=self.globals,
                                                        io=io, timestamp_callback=timestamp_callback)
        if "memories" in yaml_content:
            agent.memory_operator.from_list(yaml_content["memories"])

        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            session.add(agent_meta)
            session.commit()

        logger.debug("create suc, agent name:%s" % agent.meta.name)
        return agent

    def delete(self, agent_name: str):
        with Session(self.globals.sql_orm.engine) as session:
            session.query(AgentMeta).filter(AgentMeta.name == agent_name).delete()
            session.commit()

        logger.debug("delete suc, agent_name:%s" % agent_name)

    def get(self, agent_name: str, sandbox_id: str, io: BaseIo, timestamp_callback: Callable) -> RolePlayAgent:
        with Session(self.globals.sql_orm.engine) as session:
            results: List[AgentMeta] = session.query(AgentMeta).filter(AgentMeta.name == agent_name).\
                filter(AgentMeta.sandbox_id == sandbox_id).all()
            if len(results) == 0:
                return None

            agent_meta: AgentMeta = results[0]
            agent: RolePlayAgent = RolePlayAgent(agent_meta=agent_meta, globals=self.globals,
                                                            io=io, timestamp_callback=timestamp_callback)

            logger.debug("get suc, agent_name:%s" % agent_name)
            return agent

    def get_or_create(self, yaml_content: Dict[str, Any], io: BaseIo, timestamp_callback: Callable, sandbox_id: str) -> RolePlayAgent:
        agent_name = yaml_content.get("name", "")
        agent: RolePlayAgent = self.get(agent_name, sandbox_id, io, timestamp_callback)
        if agent is None:
            agent: RolePlayAgent = self.create(yaml_content, io, timestamp_callback)

        logger.debug("get_or_create suc, agent_name: %s" % agent_name)
        return agent

    def get_or_create_batch(self, config_path: str, io: BaseIo, timestamp_callback: Callable, sandbox_id: str) -> Dict[str, RolePlayAgent]:
        agent_dicts: [str, RolePlayAgent] = {}
        yaml_content = get_yaml_content(config_path)
        for _, agent_meta_dict in yaml_content.items():
            agent_meta_dict["sandbox_id"] = sandbox_id
            agent: RolePlayAgent = self.get_or_create(agent_meta_dict, io, timestamp_callback, sandbox_id)
            agent_dicts[agent.meta.name] = agent

        logger.debug("get_or_create_batch suc, agent cnt:%d" % len(agent_dicts))
        return agent_dicts
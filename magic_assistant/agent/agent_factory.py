from loguru import logger

from magic_assistant.agent.base_agent import BaseAgent
from magic_assistant.agent.plan.plan_agent import PlanAgent
from magic_assistant.agent.chat.chat_agent import ChatAgent
from magic_assistant.agent.execute_cmd.execute_cmd_agent import ExecuteCmdAgent
from magic_assistant.agent.role_play.role_play_agent import RolePlayAgent
from magic_assistant.utils.globals import Globals
from magic_assistant.io.base_io import BaseIo
from magic_assistant.agent.base_agent import AgentMeta
from magic_assistant.agent.knowledge_base.knowledge_base_agent import KnowledgeBaseAgent

def get_agent(agent_meta: AgentMeta, globals: Globals, io: BaseIo) -> BaseAgent:
    agent: BaseAgent = None

    if agent_meta.type == "role_play":
        agent = RolePlayAgent(agent_meta=agent_meta, globals=globals, io=io)
    elif agent_meta.type == "plan":
        agent = PlanAgent(agent_meta=agent_meta, globals=globals, io=io)
    elif agent_meta.type == "chat":
        agent = ChatAgent(agent_meta=agent_meta, globals=globals, io=io)
    elif agent_meta.type == "execute_cmd":
        agent = ExecuteCmdAgent(agent_meta=agent_meta, globals=globals, io=io)
    elif agent_meta.type == "knowledge_base":
        agent = KnowledgeBaseAgent(agent_meta=None, globals=globals, io=None)
    else:
        logger.error("unsupport agent type: %s" % agent_meta.type)
        return agent

    logger.debug("get_agent suc, agent_type:%s" % agent_meta.type)
    return agent

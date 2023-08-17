from loguru import logger

from magic_assistant.agent.base_agent import BaseAgent
from magic_assistant.agent.plan.plan_agent import PlanAgent
from magic_assistant.agent.chat.chat_agent import ChatAgent
from magic_assistant.agent.execute_cmd.execute_cmd_agent import ExecuteCmdAgent
from magic_assistant.agent.role_play.role_play_agent import RolePlayAgent
from magic_assistant.utils.globals import Globals
from magic_assistant.io.base_io import BaseIo

def get_agent(agent_type: str, globals: Globals, io: BaseIo) -> BaseAgent:
    agent: BaseAgent = None

    if agent_type == "role_play":
        agent = RolePlayAgent(globals=globals, io=io)
    if agent_type == "plan":
        agent = PlanAgent(globals=globals, io=io)
    elif agent_type == "chat":
        agent = ChatAgent(globals=globals, io=io)
    elif agent_type == "execute_cmd":
        agent = ExecuteCmdAgent(globals=globals, io=io)
    else:
        logger.error("unsupport agent type: %s" % agent_type)
        return agent

    logger.debug("get_agent suc, agent_type:%s" % agent_type)
    return agent

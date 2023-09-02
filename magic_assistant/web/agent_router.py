import json

from loguru import logger
from fastapi.websockets import WebSocket
from fastapi import APIRouter

from typing import Dict, List
from magic_assistant.utils.globals import GLOBALS
from magic_assistant.utils.utils import get_http_rsp
from magic_assistant.agent.agent_manager import AgentManager
from magic_assistant.io.websocket_io import WebsocketIo
from magic_assistant.agent.base_agent import BaseAgent
from magic_assistant.agent.agent_factory import get_agent
from magic_assistant.agent.base_agent import AgentMeta

agent_router = APIRouter()
AGENT_MANAGER = AgentManager(globals=GLOBALS)


@agent_router.post("/agent/create")
def create_agent(body: Dict):
    agent_meta = AgentMeta()
    agent_meta.from_dict(body)
    agent_meta = AGENT_MANAGER.create_v2(agent_meta=agent_meta)
    if agent_meta is None:
        logger.error("create_agent failed, input_body:%s" % body)
        return get_http_rsp(ret=-1, msg="failed")
    else:
        logger.debug("create_agent suc, agent_id:%s" % agent_meta.id)
        return get_http_rsp(data={"id": agent_meta.id})


@agent_router.post("/agent/delete")
def delete_agent(body: Dict):
    agent_meta = AgentMeta()
    agent_meta.from_dict(body)
    ret = AGENT_MANAGER.delete_v2(agent_meta=agent_meta)
    if ret == 0:
        logger.debug("delete_agent suc, agent_id:%s" % id)
        return get_http_rsp()
    else:
        logger.error("delete_agent failed, agent_id:%s" % id)
        return get_http_rsp(code=ret, msg="failed")


@agent_router.post("/agent/list")
def list(body: Dict):
    agent_meta_list: List[AgentMeta] = AGENT_MANAGER.list()
    logger.debug("list suc, agent_meta cnt:%s" % len(agent_meta_list))
    return get_http_rsp(data=agent_meta_list)

@agent_router.post("/agent/process")
def process(body: Dict):
    '''
    agent_meta: DIct,
    user_id: str,
    bucket_name: str
    person_input: str
    :param body:
    :return:
    '''
    agent_meta: AgentMeta = AgentMeta()
    agent_meta.from_dict(body["agent_meta"])
    agent: BaseAgent = get_agent(agent_meta=agent_meta, globals=GLOBALS, io=None)
    assistant_output: str = agent.process(body["person_input"])

    logger.debug("process suc")
    return get_http_rsp(data={"assistant_output": assistant_output})

@agent_router.websocket("/agent/run")
def run(websocket: WebSocket):
    await websocket.accept()
    data_str: Dict = await websocket.receive_text()
    data: Dict = json.loads(data_str)
    agent_id = data.get("id", "")
    if agent_id == "":
        logger.error("agent_id is blank")
        return

    websocket_io: WebsocketIo = WebsocketIo(websocket=websocket)
    agent: BaseAgent = AGENT_MANAGER.get_by_id(id=agent_id, io=websocket_io)
    agent.init()
    agent.run()

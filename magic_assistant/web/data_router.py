import json

from loguru import logger
from fastapi import File, UploadFile
from fastapi import APIRouter

from typing import Dict, List
from magic_assistant.utils.globals import GLOBALS
from magic_assistant.utils.utils import get_http_rsp
from magic_assistant.data.data_manager import DataManager
from magic_assistant.data.data import Data

data_router = APIRouter()

DATA_MANAGER = DataManager(globals=GLOBALS)


@data_router.post("/data/addText")
def create_agent(body: Dict):
    data: Data = Data()
    data.from_dict(body)

    ret = DATA_MANAGER.add(data)
    if ret != 0:
        logger.error("add_text suc, input_body:%s" % body)
        return get_http_rsp(ret=-1, msg="failed")
    else:
        logger.debug("add_textt suc, data_id:%s" % data.id)
        return get_http_rsp(data={"id": data.id})


@data_router.post("/data/addFile")
def add_file(file: UploadFile = File()):
    data: Data = Data()
    await data.from_upload_file(file)
    ret = DATA_MANAGER.add(data)

    if ret != 0:
        logger.error("add_file failed")
        return get_http_rsp(code=-1, msg="failed")
    else:
        logger.debug("add_file suc, data_id:%s" % data.id)
        return get_http_rsp(data={"id": data.id})


@data_router.post("/data/delete")
def delete_agent(body: Dict):
    data: Data = Data()
    data.from_dict(body)
    ret = DATA_MANAGER.delete(data)
    if ret == 0:
        logger.debug("delete suc, data_id:%s" % data.id)
        return get_http_rsp()
    else:
        logger.error("delete failed, data_id:%s" % data.id)
        return get_http_rsp(code=ret, msg="failed")


@data_router.post("/data/get")
def get_data(body: Dict):
    data_list = DATA_MANAGER.get()
    if data_list is None:
        logger.error("get failed")
        return get_http_rsp(code=-1, msg="failed")
    else:
        logger.debug("get suc")
        return get_http_rsp(data=[ data.to_dict() for data in data_list ])


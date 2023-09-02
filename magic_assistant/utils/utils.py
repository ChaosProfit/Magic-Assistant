import asyncio
import hashlib
import re
from loguru import logger
from typing import Dict, Any, List

def init_log(level="DEBUG"):
    logger.remove(handler_id=None)
    logger.add('./log/{time:YYYY-MM-DD}.log', level=level, rotation='1024 MB', encoding='utf-8')


def clean_text(text: str) -> str:
    cleaned_text = re.sub(' +', ' ', text)
    cleaned_text = cleaned_text.replace("\n ", "\n")
    cleaned_text = re.sub('\n+', '\n', cleaned_text)
    cleaned_text = re.sub('\t+', '\t', cleaned_text)
    return cleaned_text


def base_decode_llm_output(llm_output: str, key: str) -> str:
    match = re.search("<{key}>([\w\W]*?)</{key}>".format(key=key), llm_output)
    if match is None:
        return ""
    else:
        return match.group(1)


def decode_llm_output_batch(llm_output: str, key_list: List[str]) -> Dict[str, str]:
    result = {}
    for key in key_list:
        match = re.search("<{key}>([\w\W]*?)</{key}>".format(key=key), llm_output)
        if match is None:
            logger.error("re search failed, llm_output:%s, key:%s" % (llm_output, key))
            result[key] = ""
        else:
            result[key] = match.group(1)

    return result


def get_http_rsp(code=0, msg="suc", data={}):
    """
    getHttpRsp
    """
    rsp = {"code": code, "data": data, "msg": msg}
    return rsp


def get_str_hash(input_str: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(input_str.encode())
    return sha256.hexdigest()


def get_bytes_hash(input_bytes: bytes) -> str:
    sha256 = hashlib.sha256()
    sha256.update(input_bytes)
    return sha256.hexdigest()


def deep_dict_copy(src_dict: Dict, dst_dict: Dict):
    for key, value in src_dict.items():
        if key in dst_dict and value is not None:
            dst_dict[key] = value

# def wait_asyn_func_list(wait_list: List):
#     loops = asyncio.get_event_loop()
#     loops.run_until_complete(asyncio.wait(wait_list))

def syn_execute_asyn_func(future) -> Any:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    return future.result()
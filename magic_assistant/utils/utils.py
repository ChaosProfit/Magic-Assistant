import re
from loguru import logger
from typing import List, Dict
import re
from loguru import logger


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

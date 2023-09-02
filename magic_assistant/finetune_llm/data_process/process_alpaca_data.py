import json
from loguru import logger
from magic_assistant.utils.utils import get_str_hash
from typing import Callable, Dict, List

from magic_assistant.utils.globals import GLOBALS
from magic_assistant.finetune_llm.data_process.fintune_data import FinetuneData


DEFAULT_TEXT_VECTOR_LENGTH = 768

def translate_from_dict_to_fintune_data(dataset_name: str, input_dict: Dict) -> FinetuneData:
    finetune_data = FinetuneData()
    finetune_data.dataset_name = dataset_name
    finetune_data.instruction = input_dict.get("instruction", "")
    finetune_data.input = input_dict.get("input", "")
    finetune_data.output = input_dict.get("output", "")

    finetune_data.hash = get_str_hash(finetune_data.instruction + finetune_data.input + finetune_data.output)

    finetune_data.vector = GLOBALS.text_embedding.get(finetune_data.instruction)

    logger.debug("translate_from_dict_to_fintune_data suc")
    return finetune_data

def process_finetune_data_item(dataset_name: str, input_dict: Dict):
    finetune_data: FinetuneData = translate_from_dict_to_fintune_data(dataset_name, input_dict)
    is_existed = GLOBALS.vector_db_factory.is_finetune_data_existed(finetune_data.hash)
    if is_existed is True:
        return

    # finetune_data_list = GLOBALS.vector_db_factory.search_finetune_data(finetune_data.vector, score=0.95)
    # if len(finetune_data_list) > 0:
    #     compare_finetune_data:FinetuneData = finetune_data_list[0]
    #     if finetune_data.output > compare_finetune_data.output:
    #         finetune_data.data_clean_type = DATA_CLEAN_TYPE.CLEAN.value
    #         compare_finetune_data.data_clean_type = DATA_CLEAN_TYPE.OUTPUT_SHORT.value
    #
    #     return

    GLOBALS.vector_db_factory.add_finetune_data(finetune_data)
    logger.debug("process_finetune_data_item suc")


def write_json_to_file(json_dict: Dict, file_path: str):
    with open(file_path, "a+", encoding="utf-8") as f:
        f.write(json.dumps(json_dict, ensure_ascii=False))
        f.write("\n")

    logger.debug("write_json_to_file suc")


def from_pgvector_to_json_file(json_file_path: str):
    offset = 0
    limit = 100
    while True:
        offset += limit
        finetune_data_list: List[FinetuneData] = GLOBALS.vector_db_factory.search_finetune_data(offset=offset, limit=limit)
        for finetune_data in finetune_data_list:
            simple_json = finetune_data.to_simple_json()
            write_json_to_file(simple_json, json_file_path)

        if len(finetune_data_list) < limit:
            break

    logger.debug("from_pgvector_to_json_file suc")

def walk_vector_db(callback: Callable):
    offset = 0
    limit = 100
    while True:
        offset += limit
        finetune_data_list: List[FinetuneData] = GLOBALS.vector_db_factory.search_finetune_data(offset=offset, limit=limit)
        for finetune_data in finetune_data_list:
            callback(finetune_data)

        if len(finetune_data_list) < limit:
            break

    logger.debug("walk_pgvector suc")

def decode_alpaca_json_list(dir_path: str) -> int:
    import os
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)

        dataset_name = os.path.basename(dir_path)
        with open(file_path, "r") as f:
            content = f.read()
            try:
                item_list = json.loads(content)
            except Exception as e:
                logger.error("catch exception:%s, dir_path:%s" % (str(e), dir_path))
                return -1

            for item in item_list:
                process_finetune_data_item(dataset_name, item)

    logger.debug("decode_alpaca_gpt4_data_zh suc")
    return 0

def decode_alpaca_zh_jsonl(dir_path: str) -> int:
    import os
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)

        dataset_name = os.path.basename(dir_path)
        with open(file_path, "r") as f:
            for line in f:
                data_dict = json.loads(line)
                finetune_data_dict = {"instruction": data_dict.get("instruction_zh"), "input": data_dict.get("input_zh"), "output": data_dict.get("output_zh")}
                process_finetune_data_item(dataset_name, finetune_data_dict)

    logger.debug("decode_alpaca_data_gpt4_chinese suc")
    return 0

def decode_alpaca_jsonl(dir_path: str) -> int:
    import os
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)

        dataset_name = os.path.basename(dir_path)
        with open(file_path, "r") as f:
            for line in f:
                data_dict = json.loads(line)
                finetune_data_dict = {"instruction": data_dict.get("instruction"), "input": data_dict.get("input"), "output": data_dict.get("output")}
                process_finetune_data_item(dataset_name, finetune_data_dict)

    logger.debug("decode_alpaca_data_gpt4_chinese suc")
    return 0

def load(dir_path: str):
    import os
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if item in ["alpaca-gpt4-data-zh", "alpaca-zh"]:
            decode_alpaca_json_list(item_path)
        elif item == "alpaca-data-gpt4-chinese":
            decode_alpaca_zh_jsonl(item_path)
        elif item == "Open-Platypus":
            decode_alpaca_jsonl(item_path)
        else:
            logger.error("not supported yet:%s" % item)

    logger.debug("process suc")


if __name__ == "__main__":
    import sys
    from magic_assistant.utils.utils import init_log

    init_log()
    GLOBALS.init(init_models=[])
    if sys.argv[1] == "load":
        load(dir_path=sys.argv[2])
    elif sys.argv[1] == "dump":
        from_pgvector_to_json_file(sys.argv[2])
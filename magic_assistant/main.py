from signal import signal, SIGINT
from loguru import logger
import argparse
import uvicorn

from magic_assistant.utils.utils import init_log
from magic_assistant.utils.globals import GLOBALS
from fastapi import FastAPI
from magic_assistant.cli import Cli
from magic_assistant.db.orm_init import *

app = FastAPI()

def exit_func(signal_received, frame):
    print(GLOBALS.tips.get_tips().EXIT.value)
    exit(0)

def init_arg():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--agent', type=str, help='support types: create, delete, list, run')
    arg_parser.add_argument('--agent_meta', type=str, help='json str type, eg: "{}"')
    arg_parser.add_argument('--io_type', type=str, help='support types: cli, restful_api')
    arg_parser.add_argument('--type', type=str, help='support types: chat, execute_cmd, plan, role_play')
    arg_parser.add_argument('--role_play_config', type=str, help='', default="config/role_play")
    args = arg_parser.parse_args()

    logger.debug("init_arg suc")
    return args

def get_init_models(args) -> bool:
    if args.io_type == "restful_api":
        return []

    if args.io_type == "cli" and args.agent == "run" :
        return []

    return [None]

if __name__ == '__main__':
    signal(SIGINT, exit_func)
    init_log()
    args = init_arg()
    init_models = get_init_models(args=args)

    ret = GLOBALS.init(init_models=init_models)
    if ret != 0:
        logger.error("init globals failed")
        exit(-1)

    match args.io_type:
        case "cli":
            cli = Cli(globals=GLOBALS)
            cli.process_args(args)
            # cli.run(agent_type=args.agent_type, config_path=args.role_play_config)
        case "restful_api":
            from magic_assistant.web.data_router import data_router
            from magic_assistant.web.agent_router import agent_router
            app.include_router(data_router)
            app.include_router(agent_router)

            uvicorn.run(app, port=GLOBALS.config.web_config.port)
        case _:
            logger.error("unsupported io_type: %s" % args.mode)



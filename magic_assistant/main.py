from signal import signal, SIGINT
from loguru import logger
import argparse
import uvicorn

from magic_assistant.utils.utils import init_log
from magic_assistant.utils.globals import GLOBALS
from magic_assistant.web.web import app
from magic_assistant.cli import Cli


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

def get_init_model_flag(args) -> bool:
    if args.io_type == "restful_api":
        return True

    if args.io_type == "cli" and args.agent == "run" :
        return True

    return False

if __name__ == '__main__':
    signal(SIGINT, exit_func)
    init_log()
    args = init_arg()
    init_model_flag = get_init_model_flag(args=args)

    ret = GLOBALS.init(init_model=init_model_flag)
    if ret != 0:
        logger.error("init globals failed")
        exit(-1)

    match args.io_type:
        case "cli":
            cli = Cli(globals=GLOBALS)
            cli.process_args(args)
            # cli.run(agent_type=args.agent_type, config_path=args.role_play_config)
        case "restful_api":
            uvicorn.run(app, port=GLOBALS.config.web_config.port)
        case _:
            logger.error("unsupported io_type: %s" % args.mode)



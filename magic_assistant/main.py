from signal import signal, SIGINT
from loguru import logger
import argparse
import uvicorn

from magic_assistant.utils.utils import init_log
from magic_assistant.utils.globals import GLOBALS
from magic_assistant.web import app
from magic_assistant.cli import Cli


def exit_func(signal_received, frame):
    print(GLOBALS.tips.get_tips().EXIT.value)
    exit(0)

def init_arg():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--operation_type', type=str, help='support types: run, del')
    arg_parser.add_argument('--io_type', type=str, help='support types: cli, restful_api')
    arg_parser.add_argument('--agent_type', type=str, help='support types: chat, execute_cmd, plan, role_play')
    arg_parser.add_argument('--role_play_config', type=str, help='', default="config/role_play")
    args = arg_parser.parse_args()

    logger.debug("init_arg suc")
    return args

if __name__ == '__main__':
    signal(SIGINT, exit_func)
    init_log()
    ret = GLOBALS.init()
    if ret != 0:
        logger.error("init globals failed")
        exit(-1)

    args = init_arg()
    match args.io_type:
        case "cli":
            cli = Cli(globals=GLOBALS)
            cli.start_agent(agent_type=args.agent_type, config_path=args.role_play_config)
        case "restful_api":
            uvicorn.run(app, port=GLOBALS.config.web_config.port)
        case _:
            logger.error("unsupported io_type: %s" % args.mode)



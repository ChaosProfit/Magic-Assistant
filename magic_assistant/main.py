from loguru import logger
import argparse
import uvicorn

from magic_assistant.log import init_log
from magic_assistant.globals import GLOBAL_CONFIG, LLM_FACTORY, init_globals
from magic_assistant.web import app
from magic_assistant.cli import Cli


def init_arg():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--running_mode', type=str, help='support modes:cli, background')
    args = arg_parser.parse_args()

    logger.debug("init_arg suc")
    return args

if __name__ == '__main__':
    init_log()
    init_globals()
    args = init_arg()

    match args.running_mode:
        case "cli":
            cli = Cli(language_code=GLOBAL_CONFIG.misc_config.language_code, llm_factory=LLM_FACTORY)
            cli.start_loop()
        case "background":
            uvicorn.run(app, port=GLOBAL_CONFIG.web_config.port)
        case _:
            logger.error("unsupported running_mode: %s" % args.mode)


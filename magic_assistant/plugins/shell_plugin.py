# -*- coding: utf-8 -*-

from loguru import logger
import subprocess


from magic_assistant.plugins.base_plugin import BasePlugin


class ShellPlugin(BasePlugin):
    def run(self, argument: str) -> str:
        result = subprocess.run(argument, capture_output=True, shell=True, check=False)

        output = result.stdout.decode()
        logger.debug("run suc, argument:%s, output:%s" % (argument, output))
        return output
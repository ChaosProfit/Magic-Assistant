from loguru import logger
import subprocess


from magic_assistant.plugins.base_plugin import BasePlugin


class ShellPlugin(BasePlugin):
    def run(self, input: str):
        result = subprocess.run(input, capture_output=True, shell=True, check=False)

        logger.debug("run suc")
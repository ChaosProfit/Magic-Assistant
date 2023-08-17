# -*- coding: utf-8 -*-
from loguru import logger

from magic_assistant.sandbox.sandbox_manager import SandboxManager
from magic_assistant.agent.agent_factory import get_agent
from magic_assistant.agent.base_agent import BaseAgent
from magic_assistant.sandbox.sandbox import Sandbox
from magic_assistant.utils.globals import Globals
from magic_assistant.io.shell_io import ShellIo

class Cli():
    def __init__(self, globals: Globals):
        self.globals: Globals = globals
        self.io: ShellIo = ShellIo()

    def start_agent(self, agent_type: str, config_path: str) -> int:
        if agent_type == "role_play":
            return self._start_role_play_agent(config_path)
        else:
            return self._start_common_agent(agent_type)

    def _start_common_agent(self, agent_type: str) -> int:
        self.io.output(self.globals.tips.get_tips().WELCOME.value)

        agent: BaseAgent = get_agent(agent_type=agent_type, globals=self.globals, io=self.io)
        if agent is None:
            logger.error("start_agend failed")
            return -1

        agent.init()
        agent.run()

        return 0

    def _start_role_play_agent(self, config_path: str) -> int:
        sandbox_manager: SandboxManager = SandboxManager(globals=self.globals)
        sandbox: Sandbox = sandbox_manager.get_or_create(config_path, self.io)
        sandbox.start_loop()


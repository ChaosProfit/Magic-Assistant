# -*- coding: utf-8 -*-
import json
from typing import List
from loguru import logger
from rich.console import Console

from magic_assistant.sandbox.sandbox_manager import SandboxManager
from magic_assistant.agent.agent_factory import get_agent
from magic_assistant.agent.base_agent import BaseAgent, AgentMeta
from magic_assistant.sandbox.sandbox import Sandbox
from magic_assistant.utils.globals import Globals
from magic_assistant.io.shell_io import ShellIo
from magic_assistant.agent.agent_manager import AgentManager
from magic_assistant.utils.globals import GLOBALS

AGENT_MANAGER = AgentManager(globals=GLOBALS)

class Cli():
    def __init__(self, globals: Globals):
        self.globals: Globals = globals
        self.io: ShellIo = ShellIo()
        self._console = Console()

    def process_args(self, args):
        agent_meta = AgentMeta()
        agent_meta.from_str(args.agent_meta)

        if args.agent == "create":
            self.create_agent(agent_meta)
        elif args.agent == "delete":
            self.delete_agent(agent_meta)
        elif args.agent == "list":
            self.list()
        elif args.agent == "run":
            self.run(agent_meta)

    def create_agent(self, agent_meta: AgentMeta) -> int:
        agent_meta: AgentMeta = AGENT_MANAGER.create_v2(agent_meta)
        if agent_meta is None:
            self._console.print("create_agent failed")
            logger.error("create_agent failed")
        else:
            self._console.print("create_agent suc, agent_id:%s" % agent_meta.id)
            logger.debug("create_agent suc, agent_id:%s" % agent_meta.id)

    def delete_agent(self, agent_meta: AgentMeta):
        ret = AGENT_MANAGER.delete_v2(agent_meta)
        if ret == 0:
            self._console.print("delete agent:%s suc" % agent_meta.id)
            logger.debug("delete_agent suc, agent_id:%s" % id)
        else:
            self._console.print("delete agent:%s failed" % agent_meta.id)
            logger.error("delete_agent failed, agent_id:%s" % id)

    def list(self):
        agent_meta_list: List[AgentMeta] = AGENT_MANAGER.list()
        logger.debug("list suc, agent_meta cnt:%s" % len(agent_meta_list))
        if len(agent_meta_list) == 0:
            self._console.print("no agent")
        else:
            for agent_meta in agent_meta_list:
                self._console.print(agent_meta.to_dict())

    def run(self, agent_type: str, config_path: str) -> int:
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


from magic_assistant.config.agent_config import AgentConfig
from magic_assistant.utils.globals import Globals
from magic_assistant.io.base_io import BaseIo

class BaseAgent():
    # class BaseAgent(BaseModel):
    def __init__(self, globals: Globals, io: BaseIo):
        self.agent_config: AgentConfig = globals.config.agent_config
        self.globals: Globals = globals
        self.io: BaseIo = io

    agent_id: str = "default"
    current_loop_count: int = 0

    def init(self):
        raise NotImplementedError("Should be implemented")

    def run(self, person_input: str):
        raise NotImplementedError("Should be implemented")

    def process(self, person_input: str):
        raise NotImplementedError("Should be implemented")

    def output_intermediate_steps(self, output: str):
        if self.agent_config.output_intermediate_steps:
            self.io.output(output)

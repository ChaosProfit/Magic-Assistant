
from pydantic import BaseModel
from loguru import logger

from magic_assistant.prompt import PROMPT
from magic_assistant.models.llm.llm_factory import LlmFactory

from typing import Callable
class Agent(BaseModel):
    llm_factory: LlmFactory
    output_callback: Callable

    max_loop_count: int = 1
    current_loop_count: int = 0


    def run(self, input: str):
        objective = input
        context = ""
        while self.current_loop_count < self.max_loop_count:
            self.current_loop_count += 1
            prompt = PROMPT.format(objective=objective, context=context)
            output = self.llm_factory.predict(prompt)
            self.output_callback(output)
            logger.debug("prompt:%s, output:%s" % (prompt, output))

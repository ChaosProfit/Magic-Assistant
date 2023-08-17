from pydantic import BaseModel
from magic_assistant.schema.module import Module

class Chain(BaseModel):
    module_list: list[Module] = []

    def run(self):
        previous_input = ""
        for module in self.module_list:
            previous_input = module.run(previous_input)

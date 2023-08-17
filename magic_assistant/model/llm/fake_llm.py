from loguru import logger

from magic_assistant.model.llm.base_llm import BaseLlm


class FakeLlm(BaseLlm):
    def init(self):
        logger.debug("init suc")

    def run(self, input: str):
        action_format = '''<reason>{reason}</reason><action>{action}</action><argument>{argument}</argument>'''
        output = action_format.format(reason="a fake llm output", action="done", argument="")
        logger.debug("parse suc, output:%s" % input)
        return output
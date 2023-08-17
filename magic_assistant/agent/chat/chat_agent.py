from magic_assistant.agent.base_agent import BaseAgent
from magic_assistant.memory.simeple_memory import SimpleMemory
from magic_assistant.message import Message
from magic_assistant.agent.chat.prompt import build_prompt, decode_llm_output

class ChatAgent(BaseAgent):
    _memory: SimpleMemory = None

    def init(self):
        self._memory: SimpleMemory = SimpleMemory(agent_id=self.agent_id, orm_engine=self.orm_engine, memory_size=self.agent_config.memory_size)
        self._memory.load()

    def run(self):
        while True:
            message: Message = Message(self.agent_id)
            message.person_input = self.io.input()
            if message.person_input.strip(" ") == "":
                self.io.output(self.globals.tips.get_tips().USER_INPUT_IS_EMPTY.value)
                continue

            prompt = build_prompt(message.person_input, self._memory.get_history_str())

            message.assistant_output = self.llm_factory.run(prompt)
            self._memory.add_message(message)
            self.io.output(message.assistant_output)

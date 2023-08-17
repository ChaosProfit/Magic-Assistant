from magic_assistant.agent.base_agent import BaseAgent
from magic_assistant.memory.simeple_memory import SimpleMemory
from magic_assistant.message import Message
from magic_assistant.agent.execute_cmd.prompt import build_prompt, decode_llm_output
from magic_assistant.action.action import Action
from magic_assistant.plugins.provided_plugins import PROVIDED_PLUGINS


class ExecuteCmdAgent(BaseAgent):
    _memory: SimpleMemory = None

    def init(self):
        self._memory: SimpleMemory = SimpleMemory(agent_id=self.agent_id, orm_engine=self.orm_engine, memory_size=self.agent_config.memory_size)
        # self._memory.load()

    def run(self) -> int:
        while True:
            message: Message = Message(self.agent_id)
            message.person_input = self.io.input()
            if message.person_input.strip(" ") == "":
                self.io.output(self.globals.tips.get_tips().USER_INPUT_IS_EMPTY.value)
                continue

            action_result = ""
            if len(self._memory.get_messages()) > 0:
                action_result = self._memory.get_messages()[-1].action_result.replace("\n", " ")
            prompt = build_prompt(message.person_input, PROVIDED_PLUGINS, self._memory.get_history_str_with_result(), \
                                  action_result)
            message.assistant_output = self.llm_factory.run(prompt)
            self._memory.add_message(message)

            action: Action = decode_llm_output(message.assistant_output)
            if action is None:
                self.output_intermediate_steps("failed to decode command from the ai output:\n%s" % message.assistant_output)
                self._memory.add_message(message)
                continue

            ret = action.execute()
            if ret != 0:
                self.output_intermediate_steps("execute cmd failed, try again.")
                self._memory.add_message(message)
                continue

            message.action_result = action.result
            self._memory.add_message(message)
            self.output_intermediate_steps("%s:\n%s" % (self.globals.tips.get_tips().CURRENT_PLAN_EXECUTE_RESULT.value, message.action_result))



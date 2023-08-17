from loguru import logger

from magic_assistant.agent.plan.sub_agents.execute_action.prompt import build_prompt, decode_llm_output

from magic_assistant.action.action import Action
from magic_assistant.message import Message
from magic_assistant.agent.base_agent import BaseAgent

class ExecuteActionAgent(BaseAgent):
    def init(self) -> int:
        return 0

    def run(self, plan_object: str, plan_item: str) -> Action:
        self.output_intermediate_steps("%s:%s" % (self.globals.tips.get_tips().CURRENT_EXECUTING_PLAN.value, plan_item))

        prompt = build_prompt(plan_item, plan_object)
        llm_output = self.globals.llm_factory.run(prompt)
        action: Action = decode_llm_output(llm_output)
        if action is None:
            self.io.output(self.globals.tips.get_tips().FAILED.value)
            logger.error("agent run failed, failed to get an action from the plan item:%s" % plan_item)
            return action

        if self.agent_config.user_confirm_and_adjust:
            self.io.output('Going to execute this plugin, press "Enter" to continue. Or input your adjustment and press "Enter"')
            action = self.person_adjust(action, plan_object, plan_item)

        ret = action.execute()
        if ret == -1:
            self.io.output(self.globals.tips.get_tips().FAILED.value)
            logger.error("action execute failed")
            return action

        self.output_intermediate_steps("%s:\n%s" % (self.globals.tips.get_tips().CURRENT_PLAN_EXECUTE_RESULT.value, action.result))
        return action

    def person_adjust(self, action: Action, plan_object: str, plan_item: str) -> Action:
        while True:
            self.output_intermediate_steps(
                "Prepare to execute action, \nplugin:\n%s\n, argument:\n%s" % (action.plugin_name, action.argument))

            message: Message = Message(self.agent_id)
            message.person_input = self.io.input()
            if message.person_input.strip(" ").strip("\n").lower() == "":
                logger.debug("user comfirmed")
                break
            else:
                logger.debug("user disagree, user input:%s" % message.person_input)

            prompt = build_prompt(plan_item=plan_item, plan_object=plan_object, person_adjustment=message.person_input)
            message.llm_output = self.globals.llm_factory.run(prompt)
            action: Action = decode_llm_output(message.llm_output)
            self.io.output(self.globals.tips.get_tips().CONTINUE_OR_ADJUST.value)

        return action

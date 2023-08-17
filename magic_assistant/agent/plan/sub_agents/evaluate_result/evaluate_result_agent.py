from loguru import logger

from magic_assistant.agent.plan.sub_agents.evaluate_result.prompt import build_prompt, decode_llm_output

from magic_assistant.agent.plan.plan import Plan
from magic_assistant.action.action import Action
from magic_assistant.agent.base_agent import BaseAgent

class EvaluateResultAgent(BaseAgent):

    def init(self) -> int:
        return 0

    def run(self, user_object: str, plan_item: str, action: Action, plan: Plan) -> int:
        prompt = build_prompt(user_object, plan_item, action)
        llm_output = self.globals.llm_factory.run(prompt)
        is_plan_completed: bool = decode_llm_output(llm_output)
        if is_plan_completed is True:
            plan.complete_the_executing_item()
        else:
            plan.fail_the_executing_item()
            logger.error("One plan item is failed")

        self.output_intermediate_steps(
            "%s:%s" % (self.globals.tips.get_tips().IF_THE_PLAN_ITEM_HAS_COMPLETED_SUC.value, is_plan_completed))


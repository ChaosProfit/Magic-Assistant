from loguru import logger


from magic_assistant.agent.plan.plan import Plan
from magic_assistant.action.action import Action
from magic_assistant.agent.base_agent import BaseAgent
from magic_assistant.agent.plan.sub_agents.execute_action.execute_action_agent import ExecuteActionAgent
from magic_assistant.agent.plan.sub_agents.evaluate_result.evaluate_result_agent import EvaluateResultAgent

from magic_assistant.agent.plan.sub_agents.make_plan.make_plan_agent import MakePlanAgent

class PlanAgent(BaseAgent):
    make_plan_agent: MakePlanAgent = None
    execute_action_agent: ExecuteActionAgent = None
    evaluate_result_agent: EvaluateResultAgent = None

    def init(self) -> int:
        self.make_plan_agent: MakePlanAgent = MakePlanAgent(globals=self.globals, io=self.io)

        self.execute_action_agent: ExecuteActionAgent = ExecuteActionAgent(globals=self.globals, io=self.io)

        self.evaluate_result_agent: EvaluateResultAgent = EvaluateResultAgent(globals=self.globals, io=self.io)
        self.make_plan_agent.init()
        self.execute_action_agent.init()
        self.evaluate_result_agent.init()

        logger.debug("init suc")
        return 0

    def run(self) -> int:
        plan: Plan = self.make_plan_agent.run()

        while True:
            while True:
                if self.current_loop_count > self.agent_config.max_loop_count:
                    self.io.output(self.globals.tips.get_tips().REACH_LOOP_COUNT.value)
                    logger.error("current_loop_count %d have achieved the max_loop_count:%d" %
                                 (self.current_loop_count, self.agent_config.max_loop_count))
                    return -1

                plan_item = plan.get_an_executable_item()
                action: Action = self.execute_action_agent.run(plan.user_object, plan_item)
                self.evaluate_result_agent.run(plan.user_object, plan_item, action, plan)

                if plan.is_completed():
                    self.io.output("%s:\n%s" % (self.globals.tips.get_tips().THE_FINAL_RESULT_IS.value, action.result))
                    logger.debug("achieved the user object")
                    break

                self.current_loop_count += 1
                logger.debug("loop_count:%d" % self.current_loop_count)

        logger.debug("run suc")
        return 0
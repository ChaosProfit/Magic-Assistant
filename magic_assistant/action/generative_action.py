# from pydantic import BaseModel
# from magic_assistant.model.llm.llm_factory import LlmFactory
#
# class GenerativeAction():
#
#     def __init__(self, observation: str, agent_name: str, llm_factory: LlmFactory):
#         self.observation: str = observation
#         self.agent_name: str = agent_name
#         self.llm_factory: LlmFactory = llm_factory
#         self.target_entity: str = ""
#         self.src_entity_action: str = ""

    # def __post_init__(self):
    #     if self.llm_factory is None:
    #         return
    #
    #     self.target_entity = self._get_target_entity_from_observation(self.observation)
    #     self.src_entity_action = self._get_src_entity_action(self.agent_name, self.observation)

    # def _get_target_entity_from_observation(self, content: str) -> str:
    #     prompt_template = "Extract the entity from the following conten without explanation.\n" \
    #                       "Observation: {observation}\n"
    #
    #     prompt = prompt_template.format(observation=content)
    #     entity = self.llm_factory.run(prompt)
    #     return entity
    #
    # def _get_src_entity_action(self, entity_name: str, observation: str) -> str:
    #     prompt_template = "What is the {entity_name} doing in the following observation?\n" \
    #                       "Observation: {observation}\n"
    #
    #     prompt = prompt_template.format(entity_name=entity_name, observation=observation)
    #     action_str = self.llm_factory.run(prompt)
    #
    #     return action_str
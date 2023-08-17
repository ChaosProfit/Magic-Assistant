from loguru import logger
from magic_assistant.action.action import Action

prompt_template = '''
[OBJECT]
    {object}

[CURRENT PLAN ITEM]
    {plan_item}

[CURRENT ACTION PLUGIN]
    {current_action_plugin}
    
[CURRENT ACTION ARGUMENT]
    {current_action_argument}    
    
[CURRENT RESULT]
    {current_result}    

[OUTPUT FORMAT]
    <explanation>$EXPLANATION</explanation><result>$RESULT(bool)</result>
    
Based on the above, evaluate if the current action has complete the current plan item to achieve or get closer to the object. 
'''


def build_prompt(plan_object: str, plan_item: str, action: Action) -> str:
    return prompt_template.replace("{object}", plan_object) \
        .replace("{plan_item}", plan_item) \
        .replace("{current_action_plugin}", action.plugin_name) \
        .replace("{current_action_argument}", action.argument) \
        .replace("{current_result}", action.result)


def decode_llm_output(output: str) -> bool:
    import re

    explanation_match = re.search("<explanation>([\w\W]+)</explanation>", output)
    result_match = re.search("<result>([\w\W]+)</result>", output)
    if explanation_match is None or result_match is None:
        logger.error("decode_evaluate_result_output failed, explanation_match:%s, result_match:%s" % ())
        return False

    logger.debug("decode_evaluate_result_output suc, result:%s" % result_match.group(1))
    return result_match.group(1).lower() == "true"

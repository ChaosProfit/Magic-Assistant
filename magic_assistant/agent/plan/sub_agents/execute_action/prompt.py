import re
from loguru import logger
from magic_assistant.action.action import Action

prompt_template = '''
[OBJECT]
    {plan_object}
{person_adjustment_section}

[CURRENT PLAN ITEM]
    {plan_item}

[OUTPUT ACTION FORMAT]
    <plugin>
    $PLUGIN
    </plugin>
    <argument>
    $ARGUMENT
    </argument>

Based on the above, output an action to achieve the object or get closer to the object.{take_consideration_of_person_adjustment_section}
'''

def build_prompt(plan_item: str, plan_object: str, person_adjustment: str = "") -> str:
    if person_adjustment == "":
        person_adjustment_section = ""
        take_consideration_of_person_adjustment_section = ""
    else:
        from magic_assistant.agent.plan.prompt_tips import person_adjustment_section, \
            take_consideration_of_person_adjustment_section

    return \
        prompt_template.replace("{person_adjustment_section}", person_adjustment_section) \
            .replace("{take_consideration_of_person_adjustment_section}",
                     take_consideration_of_person_adjustment_section) \
            .replace("{plan_object}", plan_object) \
            .replace("{plan_item}", plan_item) \
            .replace("{person_adjustment}", person_adjustment)


def decode_llm_output(output: str) -> Action:
    plugin_match = re.search("<plugin>([\w\W]+)</plugin>", output)
    argument_match = re.search("<argument>([\w\W]+)</argument>", output)
    if plugin_match is None or argument_match is None:
        logger.error("decode_make_plan_output failed, plugin_match:%s, argument_match:%s" % ())
        return None

    action = Action(plugin_name=plugin_match.group(1).strip("\n"), argument=argument_match.group(1))

    logger.debug("decode_output_action_output suc")
    return action

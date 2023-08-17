from loguru import logger

from magic_assistant.agent.plan.plan import Plan
from magic_assistant.plugins.provided_plugins import PROVIDED_PLUGINS

prompt_template = '''

[OBJECT]
    {plan_object}
{person_adjustment}
    
[PROVIDED PLUGINS]:
    plugin | argument
    -----------------------
    {provided_plugins}
    
[OUTPUT PLAN FORMAT]:
    <explanation>
        $EXPLANATION
    </explanation>
    <plan>
        $PLANS
    </plan>
    
[OUTPUT PLAN EG]:
    <explanation>
        The user wants to see the files in their home directory. To achieve this, we will use the Shell plugin to execute a command that lists the files in the home directory.
    </explanation>
    <plan>
        1. Use the Shell plugin to execute the command "ls ~/" to list all files in the home directory.
    </plan>
    
Based on the above, make a plan to achieve the object. Use one plugin in one item of the plan. Every plugin has a cost, so be smart and efficient.{take_consideration_of_person_adjustment_section} 
'''


def build_prompt(plan_object: str, person_adjustment: str = ""):
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
            .replace("{provided_plugins}", PROVIDED_PLUGINS) \
            .replace("{person_adjustment}", person_adjustment)


def decode_llm_output(output: str) -> Plan:
    import re
    if output.endswith("</plan>") is False:
        output = output.rstrip("\n") + "</plan>"

    explanation_match = re.search("<explanation>([\w\W]+)</explanation>", output)
    plans_match = re.search("<plan>([\w\W]+)</plan>", output)
    if explanation_match is None or plans_match is None:
        logger.error("decode_make_plan_output failed, explanation_match:%s, plans_match:%s" % (
            explanation_match, plans_match))
        return None

    explanation_str = explanation_match.group(1).strip("\n")
    plans_str = plans_match.group(1).strip("\n")
    plan = Plan(explanation=explanation_str)
    plan.from_str(plans_str)

    logger.debug("decode_make_plan_output suc")
    return plan

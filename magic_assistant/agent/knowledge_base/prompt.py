from loguru import logger

from magic_assistant.agent.plan.plan import Plan
from magic_assistant.plugin.provided_plugins import PROVIDED_PLUGINS

prompt_template = '''

[USER_QUESTION]
    {user_question}
    
[CONTEXT]
    {context}
    
[OUTPUT FORMAT]:
    <answer>
        $ANSWER
    </answer>
    
Based on the above, answer the question based on the context.
'''


def build_prompt(user_question: str, context: str):
    return prompt_template.replace("{user_question}", user_question) \
                          .replace("{context}", context)


def decode_llm_output(output: str) -> str:
    import re
    if output.endswith("</plan>") is False:
        output = output.rstrip("\n") + "</plan>"

    answer_match = re.search("<answer>([\w\W]+)</answer>", output)
    if answer_match is None:
        logger.error("decode_knowledge_base_output failed, answer_match:%s" % answer_match)
        return None

    answer = answer_match.group(1).strip("\n")

    logger.debug("decode_make_plan_output suc")
    return answer

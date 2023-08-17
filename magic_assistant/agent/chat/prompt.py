import re
from loguru import logger

from magic_assistant.action.action import Action

prompt_template = '''
[FULL CHAT HISTORY START](for context and order by time asc):
{chat_history}
[FULL CHAT HISTORY END]

[PERSON INPUT]:
    {person_input}

You are an ai assistant chatting with a person. Be smart.
'''


def build_prompt(user_object: str, chat_history: str):
    return prompt_template.replace("{person_input}", user_object). \
        replace("{chat_history}", chat_history)


def decode_llm_output(output: str) -> Action:
    plugin_match = re.search("<plugin>([\w\W]+)</plugin>", output)
    argument_match = re.search("<argument>([\w\W]+)</argument>", output)
    if plugin_match is None or argument_match is None:
        logger.error(
            "decode_make_plan_output failed, plugin_match:%s, argument_match:%s" % (plugin_match, argument_match))
        return None

    try:
        action = Action(plugin_name=plugin_match.group(1), argument=argument_match.group(1))
    except Exception as e:
        logger.error("catch exception:%s" % str(e))
        logger.error("plugin_match:%s, argument_match:%s" % (plugin_match, argument_match))
        return None

    logger.debug("decode_output_action_output suc")
    return action

# class ChatPrompt(BasePrompt):
#     def build_prompt(self, user_object: str, chat_history: str):
#         return prompt_template.replace("{person_input}", user_object). \
#             replace("{chat_history}", chat_history)
#
#     def decode_llm_output(self, output: str) -> Action:
#         plugin_match = re.search("<plugin>([\w\W]+)</plugin>", output)
#         argument_match = re.search("<argument>([\w\W]+)</argument>", output)
#         if plugin_match is None or argument_match is None:
#             logger.error("decode_make_plan_output failed, plugin_match:%s, argument_match:%s" % (plugin_match, argument_match))
#             return None
#
#         try:
#             action = Action(plugin_name=plugin_match.group(1), argument=argument_match.group(1))
#         except Exception as e:
#             logger.error("catch exception:%s" % str(e))
#             logger.error("plugin_match:%s, argument_match:%s" % (plugin_match, argument_match))
#             return None
#
#         logger.debug("decode_output_action_output suc")
#         return action

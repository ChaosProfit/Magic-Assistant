from loguru import logger

from magic_assistant.utils.utils import base_decode_llm_output
from magic_assistant.agent.plan.plan import Plan
from magic_assistant.agent.role_play.agent_react import AgentReact
from typing import List


role_play_common_prompt = \
'''
Agent's intro:
{intro}

Summarized memory:
{summarized_memory}

{observation_key_name}:
{observation}
'''

decide_next_react_type_prompt_template = \
'''
{role_play_common_prompt}

Relevant agents:
{agents_in_context}

What type of action will {agent_name} do next? Supported types are: respond, communicate, do some thing alone.
Output in the following format:
<ReactType>$REACT_TYPE</ReactType>
<Explanation>$EXPLANATION</Explanation>

Output example:
<ReactType>an react type</ReactType>
<Explanation>an explanation</Explanation>
'''

respond_prompt_template = \
'''
{role_play_common_prompt}

How will {agent_name} respond to {respond_to}, output in the following format:
<TargetAgent>$TARGET_AGENT</TargetAgent> (Fill in the target agent)
<Say>$SAY</Say> (Fill in the the words said to the target agent)

Output example:
<TargetAgent>an agent</TargetAgent>
<Say>words said to the agent</Say>
'''

communicate_prompt_template = \
'''
{role_play_common_prompt}

Relevant agents:
{agents_in_context}

Who will {agent_name} communicate and what will {agent_name} say? Do not repeat sentences you have heard and output in the following format:
<TargetAgent>$TARGET_AGENT</TargetAgent> (Fill in the target agent)
<Say>$SAY</Say> (Fill in the the words said to the target agent)

Output example:
<TargetAgent>an agent</TargetAgent>
<Say>words said to the agent</Say>
'''

do_something_prompt_template = \
'''
{role_play_common_prompt}

What type of action will {agent_name} do next? Supported plugins are: {supported_plugins}.
Output in the following format:
<Plugin>$PLUGIN</Plugin>
<Action>$ACTION</Action>
<Explanation>$EXPLANATION</Explanation>

Output example:
<Plugin>$PLUGIN</Plugin>
<Action>$ACTION</Action>
<Explanation>$EXPLANATION</Explanation>
'''

def build_decide_next_react_type_prompt(agent_name: str, intro: str, summarized_memory: str, observation: str,
                                        agents_in_context: str) -> str:
    observation_key_name = "Observation"
    prompt_template = decide_next_react_type_prompt_template.replace("{role_play_common_prompt}", role_play_common_prompt)
    prompt = prompt_template.format(intro=intro, observation_key_name=observation_key_name, agent_name=agent_name,
                                    summarized_memory=summarized_memory, observation=observation, agents_in_context=agents_in_context)

    return prompt

def decode_decide_next_react_type_output(llm_output: str) -> str:
    return base_decode_llm_output(llm_output, "ReactType")

def build_respond_prompt(agent_name: str, intro: str, summarized_memory: str, observation: str, respond_to: str) -> str:
    observation_key_name = "Dialogue history"
    prompt_template = respond_prompt_template.replace("{role_play_common_prompt}", role_play_common_prompt)
    return prompt_template.format(intro=intro, observation_key_name=observation_key_name, agent_name=agent_name,
                                  summarized_memory=summarized_memory, observation=observation, respond_to=respond_to)


def decode_respond_output(llm_output: str, src_agent: str, respond_to: str) -> AgentReact:
    agent_react: AgentReact = AgentReact()
    agent_react.react_type = "respond"
    agent_react.src_entity = src_agent
    agent_react.target_entity = respond_to
    agent_react.react_content = base_decode_llm_output(llm_output, "Say")

    return agent_react

def build_communicate_prompt(agent_name: str, intro: str, summarized_memory: str, observation: str, agents_in_context: str) -> str:
    observation_key_name = "Observation"
    prompt_template = communicate_prompt_template.replace("{role_play_common_prompt}", role_play_common_prompt)
    return prompt_template.format(intro=intro, observation_key_name=observation_key_name, agent_name=agent_name,
                                  summarized_memory=summarized_memory, observation=observation, agents_in_context=agents_in_context)


def decode_communicate_output_batch(llm_output: str, src_entity: str) -> List[AgentReact]:
    agent_react_list: List[AgentReact] = []
    flag = "</Say>"
    flag_cnt = llm_output.count(flag)
    if flag_cnt == 0:
        logger.error("decode_communicate_output_batch failed, no flag:%s found" % flag)
        return agent_react_list
    elif flag_cnt == 1:
        agent_react = decode_communicate_output(llm_output, src_entity)
        agent_react_list.append(agent_react)
    else:
        section_list = llm_output.split(flag)
        for section in section_list:
            section = section.strip(" ").strip("\n").strip("\t")
            if len(section) == 0:
                continue

            section = section + flag
            agent_react = decode_communicate_output(section,  src_entity)
            agent_react_list.append(agent_react)

    return agent_react_list

def decode_communicate_output(llm_output: str, src_entity: str) -> AgentReact:
    agent_react: AgentReact = AgentReact()
    agent_react.react_type = "communicate"
    agent_react.src_entity = src_entity
    agent_react.target_entity = base_decode_llm_output(llm_output, "TargetAgent")
    agent_react.react_content = base_decode_llm_output(llm_output, "Say")

    return agent_react

def build_do_something_prompt(agent_name: str, intro: str, status: str, summarized_memory: str, observation: str,
                                        agents_in_context: str, supported_plugins: str) -> str:
    observation_key_name = "Observation"
    prompt_template = communicate_prompt_template.replace("{role_play_common_prompt}", role_play_common_prompt)

    return prompt_template.format(intro=intro, observation_key_name=observation_key_name, agent_name=agent_name, status=status,
                                  summarized_memory=summarized_memory, observation=observation, agents_in_context=agents_in_context,
                                  supported_plugins=supported_plugins)

def decode_do_something_output(output: str) -> Plan:
    pass


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

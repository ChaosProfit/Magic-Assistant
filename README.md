# Intro
Magic-Assistant is an open source AI agent framework. You can use it to develop multiple types of agent. Now support 4
types of agent:
## chat
Chat agent chats with you like a human. It is the most normal and simple type.
## execute_cmd
Execute cmd agent uses built-in plugins to try to accomplish your task. This agent type applies to simple tasks which 
can be accomplished by one plugin.
## plan
Plan agent makes a plan and use built-in plugins to execute plan items according to try to accomplish your task. Agent evaluate 
the result of execution and adjust plan if necessary. This agent type applies to complicated tasks which can not be 
accomplished by one plugin.
## role_play
Role play agent usually does not work alone. Each agent has its own name, role and memory. They coordinate with each other in 
your defined sandbox. This agent type is inspired by "Generative Agents: Interactive Simulacra of Human Behavior"
(https://arxiv.org/abs/2304.03442).

# Install
Magic-Assistant supports two installation types: metal and docker.
## llm
Magic-Assistant has been developed and tested with the model 'vicuna'(https://github.com/lm-sys/FastChat.git). You need to 
prepare the llm model in advance and configure the llm model path in the config/magic_assistant.yml. More llm modules will
be integrated. If you want to use a llm which has not been integrated yet, you can integrate it yourself in the magic_assistant/model/llm
directory.

## metal
1, Setup your own python environment, require python3.10+. For example, execute "conda create -n mojing python=3.10" in shell;
2, Install python packages. In shell, cd to the directory of Magic-Assistant and execute " pip3 install -e .".
## docker
The Magic-Assistant docker image has already installed the python dependencies and Magic-Assistant and starts up in restful_api mode.
If you want to use it in cli mode, you can execute "docker exec -ti $docker_name /bin/bash" and execute "python3 -m magic_assistant.main $ args".


# usage
Magic-Assistant supports two usage types: cli and restful_api. If you want to use or test Magic-Assistant in shell, choose the
cli type. If you want to integrate Magic-Assistant into own products, choose the restful_api type.
## cli
Execute "python3 -m magic_assistant.main --help" to show the supported args. Refer to the examples in the "Magic-Assistant/examples"
directory. For example, you can execute "python3 -m magic_assistant.main --gui_type cli --agent_type plan" to start a plan agent
## restful api
Will support soon.
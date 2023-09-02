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

# Environment
We have test Magic-Assistant in ubuntu22.04, rtx4090, cuda-11.7 and pytorch2.0.1. Ubuntu20.04+ should work. GPUS which hava 
more than 24+GB memory should work. 

If you encounter problems when you use Magic-Assistant in other environments, you can connect me.

# Install
Magic-Assistant supports two installation types: metal and docker.
## llm
Magic-Assistant has been developed and tested with the model 'vicuna'(https://github.com/lm-sys/FastChat.git). You need to 
prepare the llm model in advance and configure the llm model path in the config/magic_assistant.yml. More llm modules will
be integrated. If you want to use a llm which has not been integrated yet, you can integrate it yourself in the magic_assistant/model/llm
directory.

## pip
Execute "pip3 install magic_assistant" to install directly. Python is newer than 3.10. 
## docker
The mojingsmart/magic-assistant:latest docker image has already installed the python dependencies and Magic-Assistant and starts up in restful_api mode.
You can connect with it by http and websocket clients.

If you decide to use Magic-Assistant in docker, you should execute the following shell cmds to install nvidia dependencies
and configure the system:<br />
1, sudo apt-get update;<br />
2, sudo apt-get install -y nvidia-container-toolkit;<br />
3, sudo nvidia-ctk runtime configure --runtime=docker;<br />
4, sudo systemctl restart docker;<br />
5, sudo reboot.<br />

You can start the magic-assistant docker in the following methods:
1, cd $Magic-Assistant;<br />
2, docker compose -f deployment/docker-compose.yml up -d magic-assistant.<br />

## compile source
1, Setup your own python environment, require python3.10+. For example, execute "conda create -n mojing python=3.10" in shell;<br />
2, Install python packages. In shell, cd to the directory of Magic-Assistant and execute " pip3 install -e .".<br />

# client
Magic-Assistant supports two types of client: cli and restful_api. If you want to use or test Magic-Assistant in shell, choose the
cli type. If you want to integrate Magic-Assistant into own products, choose the restful_api type.
## cli
Execute "python3 -m magic_assistant.main --help" to show the supported args. Refer to the examples in the "Magic-Assistant/examples"
directory. For example, you can execute "python3 -m magic_assistant.main --agent run --io_type cli --agent_meta '{"type": $AGENT_TYPE}'" 
to start an agent.
## restful api
Execute "python3 -m magic_assistant.main --io_type restful_api --agent run" to start magic_assistant in restful_api mode. You can use
http or websocket to communicate with magic_assistant. 

# llm
## mojing-llm
### data
We have collect and clean data from the following datasets: alpaca-gpt4-data-zh, alpaca-data-gpt4-chinese and Open-Platypus.<br />
The data is stored in https://huggingface.co/datasets/Guanglong/mojing-llm.<br />
### model
We have also fine-tuned llama2 on this dataset. We have released two types of llm in huggingface:
7B(https://huggingface.co/Guanglong/mojing-llm-7b) and 13B(https://huggingface.co/Guanglong/mojing-llm-13b). <br />
The 7B and 13B llm can run on consumer-grade GPUS like RTX4090, RTX3090 and so on.
## llm api 
We will import the api of openai and other llm providers(like baidu) soon. Users could use these apis without self-hosted gpus.
## others llm
Most llama/llama2 series llm(like vicuna like platypus2) can be used.

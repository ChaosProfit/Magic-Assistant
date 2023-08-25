# Introduction

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

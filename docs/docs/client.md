# Client
Magic-Assistant supports two types of client: cli and restful_api. If you want to use or test Magic-Assistant in shell, choose the
cli type. If you want to integrate Magic-Assistant into own products, choose the restful_api type.
## Cli
Execute "python3 -m magic_assistant.main --help" to show the supported args. Refer to the examples in the "Magic-Assistant/examples"
directory. For example, you can execute "python3 -m magic_assistant.main --agent run --io_type cli --agent_meta '{"type": $AGENT_TYPE}'" 
to start an agent.
## Restful Api
Execute "python3 -m magic_assistant.main --io_type restful_api --agent run" to start magic_assistant in restful_api mode. You can use
http or websocket to communicate with magic_assistant. 
For the restful_api detail, you can refer to [restful api](./client/restful_api.md).

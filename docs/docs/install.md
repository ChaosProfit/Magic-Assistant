# Install
Magic-Assistant supports two installation types: metal and docker.
## pip
Execute "pip3 install magic_assistant" to install directly. Python is newer than 3.10. 
## docker
The mojingsmart/magic-assistant:latest docker image has already installed the python dependencies and Magic-Assistant and starts up in restful_api mode.
You can connect with it by http and websocket clients.

If you decide to use Magic-Assistant in docker, you should execute the following shell cmds to install nvidia dependencies
and configure the system:
1, sudo apt-get update
2, sudo apt-get install -y nvidia-container-toolkit
3, sudo nvidia-ctk runtime configure --runtime=docker
4, sudo systemctl restart docker
5, sudo reboot

You can start the magic-assistant docker in the following methods:
1, cd $Magic-Assistant
2, docker compose -f deployment/docker-compose.yml up -d magic-assistant

## compile source
1, Setup your own python environment, require python3.10+. For example, execute "conda create -n mojing python=3.10" in shell;

2, Install python packages. In shell, cd to the directory of Magic-Assistant and execute " pip3 install -e .".

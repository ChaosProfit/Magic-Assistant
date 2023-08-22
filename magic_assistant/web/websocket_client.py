from websockets.sync.client import connect
import json
from magic_assistant.io.shell_io import ShellIo

class CliToWebsocketClient():
    def __init__(self, server_endpoint: str, agent_id: str):
        self.ws = connect(server_endpoint)
        self._shell_io = ShellIo()
        self._agent_id = agent_id
        self._connect_server(agent_id)

    def _connect_server(self, agent_id: str):
        payload = {"id": agent_id}
        self.ws.send(json.dumps(payload))

    def output(self):
        recv_data = self.ws.recv()
        self._shell_io.output(recv_data)

    def input(self):
        content = self._shell_io.input()
        payload = {"id": self._agent_id, "content": content, "user_id": "default"}
        self.ws.send(json.dumps(payload))

if __name__ == "__main__":
    import sys

    server_endpoint = sys.argv[1]
    agent_id = sys.argv[2]

    cli_to_websocket_client = CliToWebsocketClient(server_endpoint=server_endpoint, agent_id=agent_id)
    while True:
        cli_to_websocket_client.output()
        cli_to_websocket_client.input()
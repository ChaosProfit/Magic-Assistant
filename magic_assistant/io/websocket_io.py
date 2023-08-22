import json
from typing import Dict
from loguru import logger
from fastapi.websockets import WebSocket
from magic_assistant.io.base_io import BaseIo


class WebsocketIo(BaseIo):
    def __init__(self, websocket: WebSocket):
        self._websocket: WebSocket = websocket

    async def input(self) -> str:
        role = "USER"
        ret = await self._websocket.send_text(f"[bold]{role}: ")
        receive_data = await self._websocket.receive()
        if "text" in receive_data:
            receive_data_str: str = receive_data.get("text", "")
        else:
            logger.error("input failed, invalid person_input type")
            return ""

        receive_data = json.loads(receive_data_str)
        content = receive_data.get("content", "")
        logger.debug("input suc, content:%s" % content)
        return content

    async def output(self, content: str):
        role = "MAGIC_ASSISTANT"
        await self._websocket.send_text(f"[bold]{role}:")
        await self._websocket.send_text(f"{content}")

        logger.debug("output suc, input:%s" % input)
        return 0

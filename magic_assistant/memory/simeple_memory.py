from loguru import logger
# from pydantic import BaseModel
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from magic_assistant.message import Message


class SimpleMemory():
    def __init__(self, agent_id: str, orm_engine: Engine, memory_size: int):
        self.agent_id: str = agent_id
        self.orm_engine: Engine = orm_engine
        self.memory_size: int = memory_size

        self._message_list: list = []

        self._row_template = "{person_input}  |  {assistant_output}  |  {timestamp}\n"
        self._row_template2 = "\t<UserInput>\n\t{person_input}\n\t</UserInput>\n\t<AssistantOutput>\n\t{assistant_output}\n\t</AssistantOutput>\n\t<timestamp>\n\t{timestamp}\n\t</timestamp>\n"
        self._row_template3 = "\tUserInput:\n{person_input}\nAssistantOutput\n{assistant_output}\n"


    def get_messages(self) -> list[Message]:
        return self._message_list

    def load(self) -> int:
        if self.orm_engine is None:
            logger.error("engine is none")
            return -1

        with Session(self.orm_engine) as session:
            self._message_list: list = session.query(Message).filter(Message.agent_id==self.agent_id).order_by(Message.timestamp.desc()).limit(self.memory_size).all()
            self._message_list.reverse()
        logger.debug("load suc, memory_size:%d" % len(self._message_list))
        return 0

    def add_message(self, message: Message) -> int:
        self._message_list.append(message)
        logger.debug("add message suc")

        if self.orm_engine is None:
            logger.debug("add_message suc, but not persistent")
            return 0

        with Session(self.orm_engine, expire_on_commit=False) as session:
            session.add(message)
            session.commit()

        logger.debug("add_message suc")
        return 0

    def get_history_str_old(self) -> str:
        history_str = ""
        start_row_str = self._row_template.format(person_input="user input", assistant_output="assistant output", timestamp="timestamp")
        sepration = "------------------------------------------------\n"

        history_str += start_row_str
        history_str += sepration

        for message in self._message_list:
            row_str = self._row_template.format(person_input=message.person_input, assistant_output=message.assistant_output, timestamp=message.timestamp)
            history_str += row_str

        logger.debug("get_history_str")
        return history_str

    def get_history_str(self) -> str:
        history_str = ""

        for message in self._message_list[-1-self.memory_size:]:
            history_str += "\tperson:\n\t\t%s\n" % message.person_input
            history_str += "\tassistant:\n\t\t%s\n" % message.assistant_output

        logger.debug("get_history_str suc")
        return history_str

    def get_history_str_with_result(self) -> str:
        history_str = ""

        for message in self._message_list[-1-self.memory_size:]:
            history_str += "\tperson:\n\t\t%s\n" % message.person_input
            history_str += "\tassistant:\n\t\t%s\n" % message.assistant_output
            history_str += "\taction result:\n\t\t%s\n" % message.action_result

        logger.debug("get_history_str_with_result suc")
        return history_str

'''
I want to know how to list the files in the home directory.
'''
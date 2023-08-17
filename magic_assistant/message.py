import time
from sqlalchemy import Column, Text, String, BigInteger
from magic_assistant.db.orm import BASE


class Message(BASE):
    __tablename__ = "message"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    agent_id = Column(String)
    person_input = Column(Text)
    assistant_output = Column(Text)
    action_result = Column(Text)
    timestamp = Column(BigInteger)

    def __init__(self, agent_id: str = ""):
        self.agent_id = agent_id
        self.timestamp = int(time.time()*1000)

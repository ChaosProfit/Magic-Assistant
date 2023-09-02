import time

from fastapi import UploadFile
import uuid
from enum import Enum
from typing import Dict, List
from sqlalchemy import Column, String, BigInteger, Integer

from magic_assistant.utils.utils import get_bytes_hash
from magic_assistant.db.orm import BASE
from magic_assistant.utils.utils import syn_execute_asyn_func


class DATA_TYPE(Enum):
    TEXT = "text"
    DOC = "doc"


class Data(BASE):
    __tablename__ = "data"
    id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    bucket_name = Column(String, nullable=False, primary_key=True)
    name = Column(String, primary_key=True)
    hash = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    # content = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)

    def __init__(self):
        self.id = uuid.uuid1().hex
        self.bucket_name = "default"
        self.user_id = "default"
        self.add_timestamp = int(time.time() * 1000)
        self.file_bytes: bytes = None
        self.content = ""
        self.content_list: List[str] = []

    def split_content(self):
        self.content_list = self.content.split("/n")

    def from_dict(self, data_dict: Dict):
        self.id = data_dict.get("id", "")
        self.user_id = data_dict.get("user_id", "")
        self.bucket_name = data_dict.get("bucket_name", "")
        self.name = data_dict.get("name", "")
        self.type = data_dict.get("type", "")
        self.content = data_dict.get("content", "")

    def to_dict(self) -> Dict:
        '''
            id = Column(String, nullable=False)
    user_id = Column(String, nullable=False, primary_key=True)
    bucket_name = Column(String, nullable=False, primary_key=True)
    name = Column(String, primary_key=True)
    hash = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    add_timestamp = Column(BigInteger, nullable=False)
        :return:
        '''

        output_dict = {}
        output_dict["id"] = self.id
        output_dict["user_id"] = self.user_id
        output_dict["bucket_name"] = self.bucket_name
        output_dict["name"] = self.name
        output_dict["type"] = self.type
        output_dict["content"] = self.content
        output_dict["size"] = self.size
        output_dict["add_timestamp"] = self.add_timestamp

        return output_dict

    def from_upload_file(self, upload_file: UploadFile):
        self.file_bytes = syn_execute_asyn_func(upload_file.read())
        # self.file_bytes = syn await upload_file.read()
        self.type = DATA_TYPE.DOC.value
        self.size = upload_file.size
        self.name = upload_file.filename
        self.hash = get_bytes_hash(self.file_bytes)


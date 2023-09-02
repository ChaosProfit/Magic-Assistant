import time
import uuid
import hashlib

from typing import List

from magic_assistant.utils.utils import get_str_hash

class Vector():
    def __init__(self, user_id: str, bucket_name: str, data_id: str, content: str = "", vector: List[float] = []):
        self.id: str = uuid.uuid1().hex
        self.user_id: str = user_id
        self.bucket_name: str = bucket_name
        self.hash: str = ""
        self.data_id: str = data_id
        self.content: str = content
        self.vector: List[float] = vector
        self.timestamp: int = int(time.time()*1000)

        self.score = 0.0

        sha256 = hashlib.sha256()
        sha256.update(self.content.encode())
        self.hash = sha256.hexdigest()

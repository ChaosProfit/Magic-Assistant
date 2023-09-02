from pydantic import BaseModel


class BasePlugin(BaseModel):
    def run(self, argument: str):
        raise NotImplementedError("this method shold ")


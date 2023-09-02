from pydantic import BaseModel

class BaseConfig(BaseModel):
    def parse(self, web_config_dict: dict):
        for key, value in web_config_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

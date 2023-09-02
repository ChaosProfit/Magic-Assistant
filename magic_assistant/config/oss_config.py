from magic_assistant.config.base_config import BaseConfig

class OssConfig(BaseConfig):
    access_key: str = ""
    secret_key: str = ""
    endpoint: str = ""
    default_bucket: str = "default"
    type: str = ""


    # def parse(self, oss_config_dict: dict):
    #     for key, value in oss_config_dict.items():
    #         if key in self.__dict__ and value is not None:
    #             self.__dict__[key] = value
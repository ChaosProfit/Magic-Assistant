import yaml
from pydantic import BaseModel

from magic_assistant.config.llm_config import LlmConfig
from magic_assistant.config.web_config import WebConfig
from magic_assistant.config.misc_config import MiscConfig

class GlobalConfig(BaseModel):
    llm_config: LlmConfig = LlmConfig()
    web_config: WebConfig = WebConfig()
    misc_config: MiscConfig = MiscConfig()

    def parse(self, config_file_path: str="./config.yml"):
        with open(config_file_path, 'r') as f:
            file_content = f.read()
            yaml_config_content = yaml.load(file_content, yaml.Loader)
            self.llm_config.__dict__ = yaml_config_content["llm"]
            self.web_config.__dict__ = yaml_config_content["web"]
            self.misc_config.__dict__ = yaml_config_content["misc"]

            pass

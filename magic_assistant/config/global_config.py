from loguru import logger
import yaml
from pydantic import BaseModel

from magic_assistant.config.model_config import ModelConfig
from magic_assistant.config.web_config import WebConfig
from magic_assistant.config.agent_config import AgentConfig
from magic_assistant.config.misc_config import MiscConfig
from magic_assistant.config.postgre_config import PostgreConfig
from magic_assistant.config.vector_db_config import VectorDbConfig

class GlobalConfig():
    model_config: ModelConfig = ModelConfig()
    web_config: WebConfig = WebConfig()
    agent_config: AgentConfig = AgentConfig()
    misc_config: MiscConfig = MiscConfig()
    postgre_config: PostgreConfig = PostgreConfig()
    vector_db_config: VectorDbConfig = VectorDbConfig()

    def parse(self, config_file_path: str="./config/magic_assistant.yml") -> int:
        from magic_assistant.config.utils import get_yaml_content
        yaml_content = get_yaml_content(config_file_path)

        try:
            if len(yaml_content) == 0:
                logger.error("yaml content is blank")
                return -1

            self.web_config.__dict__ = yaml_content["web"]
            self.agent_config.__dict__ = yaml_content["agent"]
            self.misc_config.__dict__ = yaml_content["misc"]
            self.postgre_config.__dict__ = yaml_content["db"]["postgre"]
            self.vector_db_config.parse(yaml_content["vector"])
            self.model_config.parse(yaml_content["model"])

            logger.debug("parse config suc")
            return 0
        except Exception as e:
            logger.error("parse config failed, catch exception:%s" % str(e))
            return -1

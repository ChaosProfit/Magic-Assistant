from pydantic import BaseModel
import yaml
from loguru import logger

from magic_assistant.agent.role import Role

class RoleConfig(BaseModel):
    config_path: int = 0

    def process(self) -> list[Role]:
        role_list = []
        try:
            with open(self.config_path, 'r') as f:
                file_content = f.read()
                yaml_config_content = yaml.load(file_content, yaml.Loader)

            logger.debug("parse config suc")
            return role_list
        except Exception as e:
            logger.error("parse config failed, catch exception:%s" % str(e))
            return role_list
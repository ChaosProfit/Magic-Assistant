import os
from loguru import logger
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from magic_assistant.sandbox.sandbox import Sandbox, SandboxMeta
from magic_assistant.utils.globals import Globals
from magic_assistant.io.base_io import BaseIo
from magic_assistant.config.utils import get_yaml_content

class SandboxManager():
    def __init__(self, globals: Globals):
        self.globals: Globals = globals

    def create(self, role_play_config_path: str, io: BaseIo) -> Sandbox:
        config_file_path = os.path.join(role_play_config_path, "sandbox.yml")
        yaml_content = get_yaml_content(config_file_path)
        if len(yaml_content) == 0:
            logger.error("get yaml content failed, config_file_path:%s" % config_file_path)
            return None

        sandbox_name = yaml_content.get("name", "")
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            results = session.query(SandboxMeta).filter(SandboxMeta.name==sandbox_name).all()
            if len(results) > 0:
                logger.error("create failed, sandbox with the same name %s alreday existed" % sandbox_name)
                return None

            sandbox_meta: SandboxMeta = SandboxMeta()
            for key, value in yaml_content.items():
                if value is None:
                    continue

                sandbox_meta.__dict__[key] = value

            sandbox = Sandbox(sandbox_meta=sandbox_meta, role_play_config_path=role_play_config_path, globals=self.globals, io=io)
            session.add(sandbox_meta)
            session.commit()

            logger.debug("create suc")
            return sandbox

    def delete(self, sandbox_name: str):
        with Session(self.globals.sql_orm.engine) as session:
            session.query(Sandbox).filter(Sandbox.name == sandbox_name).delete()
            session.commit()

        logger.debug("delete suc")
    def get(self, sandbox_name: str, role_play_config_path: str, io: BaseIo) -> Sandbox:
        with Session(self.globals.sql_orm.engine) as session:
            results: List[SandboxMeta]  = session.query(SandboxMeta).filter(SandboxMeta.name==sandbox_name).all()
            if len(results) == 0:
                logger.error("get failed, no such sandbox:%s" % sandbox_name)
                return None

            sandbox_meta: SandboxMeta = results[0]
            sandbox: Sandbox = Sandbox(sandbox_meta=sandbox_meta, role_play_config_path=role_play_config_path, globals=self.globals, io=io)

        logger.debug("get suc")
        return sandbox

    def get_or_create(self, role_play_config_path: str, io: BaseIo) -> Sandbox:
        config_file_path = os.path.join(role_play_config_path, "sandbox.yml")
        yaml_content: Dict[str, Any] = get_yaml_content(config_file_path)

        sandbox_name = yaml_content.get("name", "")

        sandbox: Sandbox = self.get(sandbox_name, role_play_config_path, io)
        if sandbox is not None:
            logger.debug("get_or_create suc")
            return sandbox

        return self.create(role_play_config_path, io)
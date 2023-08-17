import json

from loguru import logger
from pydantic import BaseModel
from caseconverter import pascalcase

from magic_assistant.plugins.base_plugin import BasePlugin

class Action(BaseModel):
    plugin_name: str
    argument: str

    reason: str = ""
    plugin: BasePlugin = None
    result: str = ""

    def execute(self):
        if self.plugin is None:
            self.plugin = self.get_plugin()

        if self.plugin is None:
            logger.error("execute failed, get plugin failed")
            return -1

        self.result = self.plugin.run(self.argument)

        logger.debug("execute suc")
        return 0

    def get_plugin(self):
        try:
            plugin_class_name: str = self.plugin_name.capitalize() + "Plugin"
            plugin_file_name: str = "magic_assistant.plugins." + self.plugin_name.lower() + "_plugin"
            magic_assistant = __import__(plugin_file_name)
            plugin_python_module = eval(plugin_file_name)
            plugin_class = getattr(plugin_python_module, plugin_class_name)
            plugin_obj = plugin_class()

            logger.debug("get_plugin suc, plugin_name:%s" % self.plugin_name)
            return plugin_obj

        except Exception as e:
            logger.error("get_plugin failed, catch exception:%s" % str(e))
            return None

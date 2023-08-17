# -*- coding: utf-8 -*-

from loguru import logger
from magic_assistant.plugins.base_plugin import BasePlugin
from io import StringIO
from contextlib import redirect_stdout


class PythonPlugin(BasePlugin):
    # class PythonPlugin(BasePlugin):

    def run(self, argument: str) -> str:
        argument = self._clean_argument(argument)
        try:
            _stdout = StringIO()
            with redirect_stdout(_stdout):
                exec(argument)

            output = _stdout.getvalue()
            logger.debug("run suc, argument:%s, output:%s" % (argument, output))
            return output
        except Exception as e:
            logger.error("run failed, argument:%s, catch exception:%s" % (argument, str(e)))
            return str(e)

    def _clean_argument(self, argument: str) -> str:
        return argument.replace("\_", "_")

# if __name__ == "__main__":
#     python_plugin = PythonPlugin()
#     argument = "import os; print(os.listdir('~'))"
#     argument1 = """import random\n\ndef sort\_func(arr):\n arr.sort()\n return arr\n\nrandom\_arr = [random.randint(1, 100) for i in range(10)]\n print(sort\_func(random\_arr))"""
#     argument2 = "import random\n\ndef sort\_func(arr):\n arr.sort()\n return arr\n\nrandom\_arr = [random.randint(1, 100) for i in range(10)]\n print(sort\_func(random\_arr))"
#     argument3 = """import random\n\ndef sort\_func(arr):\n arr.sort()\n return arr\n\nrandom\_arr = [random.randint(1, 100) for i in range(10)]\n print(sort\_func(random\_arr))"""
#
#     python_plugin.run(argument3)
#     pass
from loguru import logger
from pydantic import BaseModel

class Plan(BaseModel):
    explanation: str
    user_object: str = ""
    full_items: list = []

    complete_items: list = []
    incomplete_items: list = []
    failed_items: list = []
    executing_item: str = ""

    original_plan_str: str = ""

    def from_str(self, input: str) -> int:
        self.original_plan_str = input
        try:
            self.full_items = input.split("\n")
            self.incomplete_items = self.full_items

            logger.debug("from_str suc")
            return 0
        except Exception as e:
            logger.error("from_str failed")
            logger.error("catch exception:%s" % str(e))
            return -1

    def to_str(self):
        output = "Plan:\n%s\n\nExplanation:\n%s\n" % (self.original_plan_str, self.explanation)
        return output

    def is_completed(self) -> bool:
        if len(self.incomplete_items) == 0:
            return True
        else:
            return False
    def get_an_executable_item(self) -> str:
        if self.executing_item != "":
            return ""

        if len(self.incomplete_items) == 0:
            return ""

        self.executing_item = self.incomplete_items.pop(0)
        return self.executing_item

    def complete_the_executing_item(self) -> int:
        if self.executing_item == "":
            return -1

        self.complete_items.append(self.executing_item)
        self.executing_item = ""
        return 0

    def fail_the_executing_item(self) -> int:
        if self.executing_item == "":
            return -1

        self.failed_items.append(self.executing_item)
        self.executing_item = ""
        return 0

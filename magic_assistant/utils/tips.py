from loguru import logger
from enum import Enum


class TIPS_BASE(Enum):
    ###basic_start###
    WELCOME = ""
    EXIT = ""
    REACH_LOOP_COUNT = ""
    FAILED = ""
    USER_INPUT_IS_EMPTY = ""
    EXPLANATION = ""
    CONTINUE_OR_ADJUST = ""
    ###basic_end###

    ###plan_start###
    PLAN = "Plan"
    CURRENT_EXECUTING_PLAN = ""
    CURRENT_PLAN_EXECUTE_RESULT = ""
    IF_THE_PLAN_ITEM_HAS_COMPLETED_SUC = ""
    THE_FINAL_RESULT_IS = ""
    ###plan_end###

class TIPS_EN(Enum):
    ###basic_start###
    WELCOME = "Nice to meet you, you can tell me what you want to do."
    EXIT = "Bye bye."
    REACH_LOOP_COUNT = "Have reached the max loop count of this chat."
    FAILED = "Failed to achieve you goal."
    USER_INPUT_IS_EMPTY = "The user input is empty."
    EXPLANATION = "Explanation"
    CONTINUE_OR_ADJUST = "Presss ENTER to continue or input your adjustment and press enter."
    ###basic_end###

    ###plan_start###
    PLAN = "Plan"
    CURRENT_EXECUTING_PLAN = "Current executing plan"
    CURRENT_PLAN_EXECUTE_RESULT = "Current plan execute result"
    IF_THE_PLAN_ITEM_HAS_COMPLETED_SUC = "If the plan item has completed successfully"
    THE_FINAL_RESULT_IS = "The final result is"
    ###plan_end###


from pydantic import BaseModel
class Tips(BaseModel):
    _languade_code: str
    def init(self, languade_code):
        self._languade_code = languade_code
        return 0
    def get_tips(self) -> TIPS_BASE:
        match self._languade_code:
            case "en":
                return TIPS_EN
            case _:
                logger.error("init_tips failed")
                return TIPS_BASE

# def init_tips(languade_code: str):
#     match languade_code:
#         case "en":
#             return TIPS_EN
#         case _:
#             logger.error("init_tips failed")
#             return None

# if __name__ == "__main__":
#     TIPS: TIPS_BASE = TIPS_BASE
#     TIPS = init_tips("en")
#     print("tip test:%s" % (TIPS.EXIT.value))
#     pass

# tips_en = {"welcome": "Nice to meet you, you can tell me what you want to do.",
#            "exit": "Bye bye",
#            "failed": "Failed to achieve you goal"
#            }
#
# tips = {"en": tips_en}
#
#
# def get_tip(tip: str):
#     return tips.get(GLOBAL_CONFIG.misc_config.language_code, {}).get(tip, "")


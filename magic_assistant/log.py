from loguru import logger

def init_log(level="DEBUG"):
    logger.remove(handler_id=None)
    logger.add('./log/{time:YYYY-MM-DD}.log', level=level, rotation='1024 MB', encoding='utf-8')

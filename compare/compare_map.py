from history.history import History
from logger import logger


def entered_map(history: History) -> History:
    logger.detail_info("== ENTERED MAP JOURNEY ==")
    logger.line()
    return history

import os
import sys

sys.path.append(os.getcwd())

from log import LoggerProxy

proxy = LoggerProxy("server")
logger = proxy.get_logger(daily_rotation=True)

if __name__ == "__main__":
    logger.critical("Критическая ошибка")
    logger.error("Ошибка")
    logger.debug("Отладочная информация")
    logger.info("Информационное сообщение")

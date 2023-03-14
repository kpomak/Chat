import os
import sys
from logging import INFO, FileHandler, Formatter, Logger, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler

sys.path.append(os.getcwd())

from app.config import ENCODING


class LoggerProxy(Logger):
    def get_logger(self, daily_rotation=False, _formatter=None, path=None):
        if self.name in self.manager.loggerDict:
            return self.manager.loggerDict[self.name]
        formatter = (
            Formatter("%(asctime)s :: [%(levelname)s] :: <<%(module)s>> :: %(message)s")
            if not _formatter
            else _formatter
        )

        if not path:
            log_file = os.path.join(os.getcwd(), "log", "logs", f"{self.name}.log")
        else:
            log_file = os.path.join(
                os.getcwd(), "log", "logs", f"{self.name.split('.')[0]}.log"
            )

        stream_handler = StreamHandler(sys.stderr)
        file_handler = (
            TimedRotatingFileHandler(log_file, encoding=ENCODING, interval=1, when="d")
            if daily_rotation
            else FileHandler(log_file, encoding=ENCODING)
        )

        logger = getLogger(self.name)
        logger.setLevel(INFO)

        for handler in (stream_handler, file_handler):
            handler.setFormatter(formatter)
            handler.setLevel(INFO)
            logger.addHandler(handler)

        return logger


class Log:
    def __init__(self):
        name = os.path.split(sys.argv[0])[-1]
        proxy = LoggerProxy(name)
        formatter = Formatter("%(asctime)s :: %(message)s")
        self.logger = proxy.get_logger(_formatter=formatter, path=True)
        self.logger.propagate = False

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.logger.info(func.__name__)
            return func(*args, **kwargs)

        return wrapper


if __name__ == "__main__":
    app = LoggerProxy("app", INFO)
    chat_logger = app.get_logger(False)
    logs = LoggerProxy("app")
    logs = logs.get_logger(True)
    assert chat_logger is logs
    logs.critical("Critical error")
    logs.error("Error")
    logs.debug("Debug information")
    logs.info("Information")
    logger = Log()
    logger(sum)([5, 3])

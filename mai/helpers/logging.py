import logging
from logging.handlers import RotatingFileHandler

from mai.helpers.colors import red


class Logging(object):
    _instance = None

    _formatter = logging.Formatter(
        "[%(asctime)s %(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    _logger = logging.getLogger("default")
    _logger.setLevel(logging.INFO)
    # _sh = logging.StreamHandler()
    # _sh.setLevel(logging.INFO)
    # _sh.setFormatter(_formatter)
    # _logger.addHandler(_sh)
    _fh = RotatingFileHandler("mai.log", maxBytes=1024 * 1024 * 1, backupCount=3)
    _fh.setLevel(logging.INFO)
    _fh.setFormatter(_formatter)
    _logger.addHandler(_fh)

    @classmethod
    def get_instance(cls):
        """Get the instance of the logging object, or create one if not created yet"""
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def info(self, message):
        """Log an INFO message"""
        print(message)
        self._logger.info(message)

    def error(self, message):
        """Log an ERROR message"""
        print(red("\n" + message))
        self._logger.error(message)

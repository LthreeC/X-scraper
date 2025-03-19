import logging
import sys
import threading
from typing import Dict, Optional

LOG_CONFIG = {
    "console": {
        "level": "INFO",
        "format": f"\033[32m%(asctime)s \033[33m[%(levelname)s] \033[34m%(filename)s:%(lineno)d \033[0m%(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
    },
    "file": {
        "level": "DEBUG",
        "format": f"%(asctime)s [%(levelname)s] %(name)s:%(filename)s:%(lineno)d %(message)s"
    }
}

_LOGGER_CACHE = {}
_LOGGER_LOCK = threading.RLock()


def get_logger(
        name: str = "global",
        log_path: Optional[str] = None,
        config: Optional[Dict] = None
) -> logging.Logger:
    with _LOGGER_LOCK:
        if name in _LOGGER_CACHE:
            return _LOGGER_CACHE[name]

        log_config = config or LOG_CONFIG
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        if logger.hasHandlers():
            logger.handlers.clear()

        try:
            console_handler = logging.StreamHandler(sys.stdout)
            console_level = getattr(logging, log_config["console"]["level"].upper(), logging.INFO)
            console_handler.setLevel(console_level)

            console_formatter = logging.Formatter(
                log_config["console"]["format"],
                datefmt=log_config["console"].get("datefmt", None)
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        except Exception as e:
            print(f"Warning: Could not set up console logging: {e}")

        if log_path:
            try:
                file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
                file_level = getattr(logging, log_config["file"]["level"].upper(), logging.DEBUG)
                file_handler.setLevel(file_level)

                file_formatter = logging.Formatter(
                    log_config["file"]["format"],
                    datefmt=log_config["file"].get("datefmt", None)
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"Warning: Could not set up file logging: {e}")

        _LOGGER_CACHE[name] = logger
        return logger

def attach_file_handler(logger: logging.Logger, file_path: str, config: str=None) -> None:
    log_config = config or LOG_CONFIG
    file_handler = logging.FileHandler(file_path, mode="a", encoding="utf-8")
    file_level = getattr(logging, log_config["file"]["level"].upper(), logging.DEBUG)
    file_handler.setLevel(file_level)

    file_formatter = logging.Formatter(
        log_config["file"]["format"],
        datefmt=log_config["file"].get("datefmt", None)
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
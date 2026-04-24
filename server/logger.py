"""
Logging configuration and logger factory for the voting system.
Provides centralized logging setup with file and console handlers.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console: bool = True,
    file_handler: bool = True
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # чтобы не добавлять хендлеры повторно
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if file_handler and log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_h = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_h.setFormatter(formatter)
        logger.addHandler(file_h)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def configure_root_logger(
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # очистка старых хендлеров
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def create_log_directory(log_dir: str = "logs") -> Path:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_log_filename(prefix: str = "voting_system") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.log"


class LoggerFactory:
    _loggers = {}
    _configured = False
    _level = logging.INFO
    _log_file = None

    @classmethod
    def configure(cls, log_file: Optional[str] = None, level: int = logging.INFO) -> None:
        cls._configured = True
        cls._level = level
        cls._log_file = log_file

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        if name in cls._loggers:
            return cls._loggers[name]

        logger = setup_logging(
            name=name,
            log_file=cls._log_file,
            level=cls._level
        )

        cls._loggers[name] = logger
        return logger

    @classmethod
    def close_all(cls) -> None:
        for logger in cls._loggers.values():
            for handler in logger.handlers:
                handler.close()
            logger.handlers.clear()

        cls._loggers.clear()
import logging
import os
from config import LOG_DIR, LOG_LEVEL

os.makedirs(LOG_DIR, exist_ok=True)

_LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def get_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Args:
        name: Logger name (typically module/class name).
        log_file: Optional specific log file name. Defaults to 'odysya.log'.
    """
    logger = logging.getLogger(name)
    level = _LOG_LEVEL_MAP.get(LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        main_handler = logging.FileHandler(
            os.path.join(LOG_DIR, log_file or "odysya.log")
        )
        main_handler.setFormatter(formatter)
        main_handler.setLevel(level)
        logger.addHandler(main_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    return logger

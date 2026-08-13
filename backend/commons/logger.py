import logging
import os


def get_file_handler(
    log_name: str, mode: int, formatter: logging.Formatter, save_path: str = "logs"
):
    """
    Creates and returns a file handler that appends log records to a file.

    Creates the log directory if it does not already exist, then attaches
    the given formatter and level to the handler before returning it.

    Args:
        log_name: Name of the log file (e.g., "debug.log")
        mode: Logging level constant (e.g., logging.DEBUG, logging.ERROR)
        formatter: Formatter instance that controls the log message layout
        save_path: Directory where the log file will be written (default: "logs")

    Returns:
        logging.FileHandler: Configured file handler ready to be added to a logger
    """
    os.makedirs(save_path, exist_ok=True)
    file_handler = logging.FileHandler(
        filename=os.path.join(save_path, log_name), mode="a"
    )
    file_handler.setLevel(mode)
    file_handler.setFormatter(formatter)
    return file_handler


def config_logger(logger: logging.Logger, debug_mode: bool = True):
    """
    Attaches a console handler and a debug file handler to the given logger.

    Both handlers share the same log format:
        [pid=<pid>] - [timestamp] - [module] - [LEVEL] - [message]

    The console handler streams output to stdout (useful during development).
    The file handler appends all DEBUG-and-above records to logs/debug.log.

    Args:
        logger: The logging.Logger instance to configure
        debug_mode: Reserved for future use (e.g., toggling verbosity)

    Returns:
        logging.Logger: The same logger instance, now configured with handlers
    """
    formatter = logging.Formatter(
        "[pid=%(process)s] - [%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    debug_file_handler = get_file_handler(
        log_name="debug.log", mode=logging.DEBUG, formatter=formatter
    )

    logger.addHandler(console_handler)
    logger.addHandler(debug_file_handler)
    logger.setLevel(logging.DEBUG)
    return logger


def logger(__name__):
    """
    Factory function that returns a named, fully configured logger.

    Call this at the top of every module using __name__ so that log records
    automatically include the originating module path:

        from commons.logger import logger
        logging = logger(__name__)
        logging.info("Something happened")

    Args:
        __name__: The module name (pass the built-in __name__ variable)

    Returns:
        logging.Logger: Logger configured with console + file (debug.log) handlers
    """
    logging_obj = config_logger(logging.getLogger(__name__))
    return logging_obj

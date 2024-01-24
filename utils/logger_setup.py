import os
import logging
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter

def parse_size_string(size_string):
    size_units = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3, 'TB': 1024 ** 4}
    size, unit = size_string.split()
    return int(size) * size_units[unit]

def setup_logger(log_level, enable_logs_save, log_file, log_rotation_size):

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level))

        console_handler = logging.StreamHandler()
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s %(white)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'bold_red',
                'CRITICAL': 'bold_purple',
                'DEBUG': 'cyan'
            },
            secondary_log_colors={},
            style='%'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        discord_logger = logging.getLogger('discord')
        discord_logger.setLevel(getattr(logging, log_level))
        discord_logger.addHandler(console_handler)

        discord_http_logger = logging.getLogger('discord.http')
        discord_http_logger.setLevel(getattr(logging, log_level))
        discord_http_logger.addHandler(console_handler)

        if enable_logs_save:
            logs_folder = os.path.dirname(log_file)
            os.makedirs(logs_folder, exist_ok=True)

            max_bytes = parse_size_string(log_rotation_size)
            file_handler = RotatingFileHandler(log_file, maxBytes = max_bytes, backupCount = 5)
            file_formatter = logging.Formatter('[{asctime}] [{levelname:<8}]: {message} - {filename}: {lineno}', style='{', datefmt="%Y-%m-%d %H:%M:%S")
            file_handler.setFormatter(file_formatter)

            logger.addHandler(file_handler)
            discord_logger.addHandler(file_handler)
            discord_http_logger.addHandler(file_handler)

        logger.propagate = False

    return logger

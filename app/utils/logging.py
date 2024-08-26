import logging
from logging.handlers import RotatingFileHandler
import os
from app.config import Config


def setup_logging(config: Config):
    log_level = logging.getLevelName(config.log_level.value)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    log_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "logs", "app.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Логи в консоль для отладки (закомментирован по умолчанию)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info(f"Logging setup completed. Log level: {config.log_level}")
    logging.info(f"Logs will be written to: {log_file_path}")

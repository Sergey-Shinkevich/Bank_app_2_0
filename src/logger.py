import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


def setup_logger(name):
    """Настройка логгера с гарантированным созданием папки."""
    # Создаем папку logs в корне проекта, если её нет
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Путь к файлу теперь всегда будет правильным: корень/logs/имя.log
    file_path = LOG_DIR / f"{name}.log"
    file_handler = logging.FileHandler(file_path, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger

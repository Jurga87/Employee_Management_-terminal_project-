import logging
from pathlib import Path

def get_logger() -> logging.Logger:
    Path("logs").mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("app")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("logs/app.log", encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger

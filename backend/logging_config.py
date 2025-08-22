import logging
import logging.handlers
import os
from pathlib import Path

LOG_DIR = Path("backend") / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

def setup_logging(env: str = "dev"):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if env == "dev" else logging.INFO)

    # Remove default handlers to avoid duplicates when reloading
    for h in list(logger.handlers):
        logger.removeHandler(h)

    # File handler (size-based rotation)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    logger.addHandler(file_handler)

    # Reduce noise from third-party libs if needed
    logging.getLogger("uvicorn.access").setLevel(logging.INFO if env == "dev" else logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logger.info(f"Logging initialized (env={env}, file={LOG_FILE})")


# logger.py

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import PROMPT_LOG_PATH

log_path = Path(PROMPT_LOG_PATH)
log_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("prompt_logger")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    filename=log_path,
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)

formatter = logging.Formatter('%(asctime)s,%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_prompt(prompt: str, style: str) -> None:

    try:
        clean_prompt = prompt.replace('\n', ' ').replace('\r', ' ').strip()
        clean_style = style.replace('\n', ' ').replace('\r', ' ').strip()
        logger.info(f"{clean_prompt},{clean_style}")
    except Exception as e:
        print(f"[Warning] 無法寫入日誌: {e}")
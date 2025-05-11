# cache_utils.py

import os
import time
import hashlib
from pathlib import Path
from config import CACHE_DIR

cache_dir = Path(CACHE_DIR)

def ensure_cache_dir_exists() -> None:
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[Warning] 無法建立快取目錄 {cache_dir}: {e}")

def get_hash(prompt: str, style: str, width: int, height: int, seed: int) -> str:
    normalized_input = f"{prompt.strip().lower()}_{style.strip().lower()}_{width}_{height}_{seed}"
    return hashlib.sha256(normalized_input.encode("utf-8")).hexdigest()

def get_cache_path(hash_key: str) -> Path:
    ensure_cache_dir_exists()
    return cache_dir / f"{hash_key}.png"

def clear_old_cache(days: int = 7) -> None:
    try:
        cutoff = time.time() - (days * 86400)
        for file in os.listdir(cache_dir):
            fpath = cache_dir / file
            if fpath.suffix == ".png" and fpath.is_file():
                if fpath.stat().st_mtime < cutoff:
                    fpath.unlink()
    except Exception as e:
        print(f"[Warning] 清理快取失敗: {e}")

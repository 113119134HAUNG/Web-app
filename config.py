# config.py

import yaml
from pathlib import Path

CONFIG_FILE = Path("config.yaml")

if not CONFIG_FILE.exists():
    raise FileNotFoundError("找不到 config.yaml，請確認檔案是否已上傳或在正確目錄中")

try:
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
except yaml.YAMLError as ye:
    raise RuntimeError(f"YAML 格式錯誤：請檢查 config.yaml 語法\n詳細錯誤：{ye}")
except Exception as e:
    raise RuntimeError(f"讀取 config.yaml 發生未知錯誤：{e}")

REQUIRED_KEYS = [
    "model_name", "cache_dir", "log_path",
    "default_width", "default_height",
    "prompt_presets", "negative_prompt"
]

missing_keys = [k for k in REQUIRED_KEYS if k not in cfg]
if missing_keys:
    raise KeyError(f"config.yaml 缺少必要欄位：{', '.join(missing_keys)}")

# 配置變數
MODEL_PATH = cfg["model_name"]
CACHE_DIR = cfg["cache_dir"]
PROMPT_LOG_PATH = cfg["log_path"]
DEFAULT_WIDTH = cfg["default_width"]
DEFAULT_HEIGHT = cfg["default_height"]
PROMPT_PRESETS = cfg["prompt_presets"]
NEGATIVE_PROMPT = cfg["negative_prompt"]

# 選填欄位
FALLBACK_MODEL_NAME = cfg.get("fallback_model_name", "runwayml/stable-diffusion-v1-5")
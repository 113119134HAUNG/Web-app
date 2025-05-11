# config.py

import yaml

with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

MODEL_NAME = cfg["model_name"]
FALLBACK_MODEL_NAME = cfg.get("fallback_model_name")
CACHE_DIR = cfg["cache_dir"]
PROMPT_LOG_PATH = cfg["log_path"]
DEFAULT_WIDTH = cfg["default_width"]
DEFAULT_HEIGHT = cfg["default_height"]
PROMPT_PRESETS = cfg["prompt_presets"]

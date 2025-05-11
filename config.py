# config.py

import yaml

try:
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
except Exception as e:
    raise RuntimeError(f"無法讀取 config.yaml：{e}")

# 必要項目
MODEL_NAME = cfg["model_name"]
CACHE_DIR = cfg["cache_dir"]
PROMPT_LOG_PATH = cfg["log_path"]
DEFAULT_WIDTH = cfg["default_width"]
DEFAULT_HEIGHT = cfg["default_height"]
PROMPT_PRESETS = cfg["prompt_presets"]
NEGATIVE_PROMPT = cfg["negative_prompt"]

# 非必要項目（提供預設值）
SD3_PATH = cfg.get("safetensor_model_path")
FALLBACK_MODEL_NAME = cfg.get("fallback_model_name", "runwayml/stable-diffusion-v1-5")

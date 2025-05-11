# inference.py

import time
import torch
import requests

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from diffusers import StableDiffusionPipeline

from config import MODEL_NAME, FALLBACK_MODEL_NAME, NEGATIVE_PROMPT
from prompt_engineering import preprocess_prompt
from cache_utils import get_hash, get_cache_path
from logger import log_prompt
from comfy_client import generate_with_comfyui

COMFY_API_URL = "http://localhost:8188"

# 主模型預先載入
fallback_pipe = StableDiffusionPipeline.from_pretrained(
    FALLBACK_MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None
).to("cuda")

# fallback 模型延遲載入
def get_fallback_pipe():
    global fallback_pipe
    if fallback_pipe is None:
        fallback_pipe = StableDiffusionPipeline.from_pretrained(
            FALLBACK_MODEL_NAME,
            torch_dtype=torch.float16,
            safety_checker=None
        ).to("cuda")
    return fallback_pipe

def add_signature(image: Image.Image, text: str) -> Image.Image:
    draw = ImageDraw.Draw(image)
    font_size = 20
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # ✅ 用 textbbox 取代已棄用的 textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = image.width - text_width - 10
    y = image.height - text_height - 10

    for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill="black")

    draw.text((x, y), text, fill="white", font=font)
    return image

def generate_image(prompt: str, style: str, width: int, height: int, seed: int) -> Tuple[Image.Image, str]:
    start_time = time.time()
    try:
        full_prompt = preprocess_prompt(prompt, style)
        generator = torch.Generator(device="cuda").manual_seed(seed)
        img_hash = get_hash(full_prompt, style, width, height, seed)
        cache_path = Path(get_cache_path(img_hash))

        if cache_path.exists():
            image = Image.open(cache_path).convert("RGB")
            source = "（從快取）"
        else:
            # 試用 ComfyUI SD3
            image, source = generate_with_comfyui(prompt, width, height, seed, COMFY_API_URL)

            # 若 ComfyUI 失敗就 fallback
            if image is None:
                output = fallback_pipe(
                    prompt=full_prompt,
                    negative_prompt=NEGATIVE_PROMPT,
                    width=width,
                    height=height,
                    generator=generator
                )
                image = output.images[0]
                source = "（Fallback SD1.5 生圖）"

            image.save(cache_path)

        image = add_signature(image, f"ID:{img_hash[:8]}")
        log_prompt(full_prompt, style)

        elapsed = round(time.time() - start_time, 2)
        return image, f"✅ 成功！{source} 耗時 {elapsed} 秒"

    except Exception as e:
        return None, f"❌ 生成失敗: {e}"

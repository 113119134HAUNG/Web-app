# inference.py

import time
from pathlib import Path
from typing import Tuple

import torch
from PIL import Image
from diffusers import StableDiffusionPipeline

from config import MODEL_NAME, NEGATIVE_PROMPT
from prompt_engineering import preprocess_prompt
from cache_utils import get_hash, get_cache_path
from logger import log_prompt


pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    revision="fp16",
    safety_checker=None
).to("cuda")

def generate_image(
    prompt: str,
    style: str,
    width: int,
    height: int,
    seed: int
) -> Tuple[Image.Image, str]:

    start_time = time.time()

    if width % 64 != 0 or height % 64 != 0:
        raise ValueError("width 和 height 必須是 64 的倍數。")

    if not isinstance(seed, int):
        raise TypeError("seed 必須是整數。")

    try:
        full_prompt = preprocess_prompt(prompt, style)

        generator = torch.Generator(device="cuda").manual_seed(seed)

        img_hash = get_hash(full_prompt, style, width, height, seed)
        cache_path = Path(get_cache_path(img_hash))

        if cache_path.exists():
            image = Image.open(cache_path).convert("RGB")
            source = "（從快取）"
        else:
            output = pipe(
                prompt=full_prompt,
                negative_prompt=NEGATIVE_PROMPT,
                width=width,
                height=height,
                generator=generator
            )
            image = output.images[0]
            image.save(cache_path)
            source = "（新生成）"

        log_prompt(full_prompt, style)

        elapsed = round(time.time() - start_time, 2)
        message = f"成功！{source} 圖像生成耗時：{elapsed} 秒"

        return image, message

    except Exception as e:
        error_msg = f"生成失敗: {e}"
        return None, error_msg


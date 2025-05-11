# inference.py

import time
import torch

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from diffusers import StableDiffusionPipeline

from config import MODEL_NAME, FALLBACK_MODEL_NAME, NEGATIVE_PROMPT
from prompt_engineering import preprocess_prompt
from cache_utils import get_hash, get_cache_path
from logger import log_prompt

# 主模型預先載入
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    revision="fp16",
    safety_checker=None
).to("cuda")

# fallback 模型延遲載入
fallback_pipe = None
def get_fallback_pipe():
    global fallback_pipe
    if fallback_pipe is None:
        fallback_pipe = StableDiffusionPipeline.from_pretrained(
            FALLBACK_MODEL_NAME,
            torch_dtype=torch.float16,
            revision="fp16",
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
    text_width, text_height = draw.textsize(text, font=font)
    x = image.width - text_width - 10
    y = image.height - text_height - 10
    shadow_color = "black"
    for offset in [(1,1), (-1,-1), (1,-1), (-1,1)]:
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_color)
    draw.text((x, y), text, fill="white", font=font)
    return image

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
            try:
                output = pipe(
                    prompt=full_prompt,
                    negative_prompt=NEGATIVE_PROMPT,
                    width=width,
                    height=height,
                    generator=generator
                )
                image = output.images[0]
                source = "（主模型生成）"
            except Exception as e1:
                try:
                    fallback = get_fallback_pipe()
                    output = fallback(
                        prompt=full_prompt,
                        negative_prompt=NEGATIVE_PROMPT,
                        width=width,
                        height=height,
                        generator=generator
                    )
                    image = output.images[0]
                    source = "（Fallback 模型生成）"
                except Exception as e2:
                    return None, f"生成失敗（Fallback 亦失敗）：{e2}"

            image.save(cache_path)

        signature = f"ID:{img_hash[:8]}"
        image = add_signature(image, signature)

        log_prompt(full_prompt, style)

        elapsed = round(time.time() - start_time, 2)
        message = f"成功！{source} 圖像生成耗時：{elapsed} 秒"

        return image, message

    except Exception as e:
        return None, f"生成失敗: {e}"

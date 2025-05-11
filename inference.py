# inference.py

import time
import torch
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
from diffusers import StableDiffusionPipeline

from config import FALLBACK_MODEL_NAME, NEGATIVE_PROMPT, DEFAULT_WIDTH, DEFAULT_HEIGHT
from prompt_engineering import preprocess_prompt
from cache_utils import get_hash, get_cache_path
from logger import log_prompt
from comfy_client import generate_with_comfyui

# 預載入 SD1.5 模型（作為主模型）
fallback_pipe = StableDiffusionPipeline.from_pretrained(
    FALLBACK_MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None
).to("cuda")

def add_signature(image: Image.Image, text: str) -> Image.Image:
    draw = ImageDraw.Draw(image)
    font_size = 20
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = image.width - text_width - 10, image.height - text_height - 10
    for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill="black")
    draw.text((x, y), text, fill="white", font=font)
    return image

def generate_image(prompt: str, style: str, width: int, height: int, seed: int, model: str = "SD1.5") -> Tuple[Image.Image, str]:
    start_time = time.time()
    try:
        full_prompt = preprocess_prompt(prompt, style)
        generator = torch.Generator(device="cuda").manual_seed(seed)
        img_hash = get_hash(full_prompt, style, width, height, seed)
        cache_path = Path(get_cache_path(img_hash))

        if cache_path.exists():
            image = Image.open(cache_path).convert("RGB")
            source = "(from cache)"
        else:
            if model == "SD3 (ComfyUI)":
                image, source = generate_with_comfyui(full_prompt, width, height, seed)
                if image is None:
                    print("[⚠️] ComfyUI 呼叫失敗，自動 fallback 為 SD1.5")
                    model = "SD1.5"

            if model == "SD1.5":
                output = fallback_pipe(
                    prompt=full_prompt,
                    negative_prompt=NEGATIVE_PROMPT,
                    width=width,
                    height=height,
                    generator=generator
                )
                image = output.images[0]
                source = "(Fallback SD1.5)"

            image.save(cache_path)

        image = add_signature(image, f"ID:{img_hash[:8]}")
        log_prompt(full_prompt, style)

        elapsed = round(time.time() - start_time, 2)
        return image, f"{source} - {elapsed}s"

    except Exception as e:
        return None, f"[Error] 生成失敗: {e}"

# gradio_app.py

import gradio as gr
from inference import generate_image
from config import DEFAULT_WIDTH, DEFAULT_HEIGHT

def ui_infer(prompt, model):
    style = "default"
    width, height, seed = DEFAULT_WIDTH, DEFAULT_HEIGHT, 42
    return generate_image(prompt, style, width, height, seed, model)

with gr.Blocks() as demo:
    gr.Markdown("## Stable Diffusion App【SD1.5 / SD3 via ComfyUI】")

    with gr.Row():
        model_choice = gr.Radio(["SD1.5", "SD3 (ComfyUI)"], label="選擇模型", value="SD1.5")

    prompt_input = gr.Textbox(label="Prompt")
    generate_btn = gr.Button("開始生成")
    image_output = gr.Image(label="輸出圖像")
    status_output = gr.Textbox(label="狀態訊息")

    generate_btn.click(
        fn=ui_infer,
        inputs=[prompt_input, model_choice],
        outputs=[image_output, status_output]
    )

if __name__ == "__main__":
    demo.launch(share=True)

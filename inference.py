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
from comfy_client import generate_with_comfyui

COMFY_API_URL = "http://localhost:8188"

# fallback 模型（SD1.5）預載入
fallback_pipe = StableDiffusionPipeline.from_pretrained(
    FALLBACK_MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None
).to("cuda")

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
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = image.width - text_width - 10, image.height - text_height - 10
    for offset in [(1,1), (-1,-1), (1,-1), (-1,1)]:
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
            source = "(from cache)"
        else:
            image, source = generate_with_comfyui(full_prompt, width, height, seed, COMFY_API_URL)
            if image is None:
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
        return image, f"Success {source}, Time: {elapsed}s"

    except Exception as e:
        return None, f"Failed to generate: {e}"

# gradio_app.py

import gradio as gr
from inference import generate_image

def ui_infer(prompt, model):
    style = "default"
    width, height, seed = 512, 512, 42
    return generate_image(prompt, style, width, height, seed)

with gr.Blocks() as demo:
    gr.Markdown("## Stable Diffusion App (SD1.5 / SD3 via ComfyUI)")
    with gr.Row():
        model_choice = gr.Radio(["SD1.5", "SD3 (ComfyUI)"], label="Select Model", value="SD1.5")
    prompt_input = gr.Textbox(label="Prompt")
    generate_btn = gr.Button("Generate")
    image_output = gr.Image(label="Output Image")
    status_output = gr.Textbox(label="Status")

    generate_btn.click(fn=ui_infer, inputs=[prompt_input, model_choice], outputs=[image_output, status_output])

if __name__ == "__main__":
    demo.launch(share=True)

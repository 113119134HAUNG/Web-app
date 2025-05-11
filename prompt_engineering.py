# prompt_engineering.py

from config import PROMPT_PRESETS
import re

def preprocess_prompt(prompt: str, style: str) -> str:

    if not prompt:
        prompt = ""

    prompt = prompt.strip()
    prompt = prompt.replace("，", ",").replace("。", ".")
    prompt = re.sub(r"\s*,\s*", ", ", prompt)
    prompt = re.sub(r"\s*\.\s*", ". ", prompt)
    prompt = re.sub(r"\s{2,}", " ", prompt)

    style_prompt = PROMPT_PRESETS.get(style, "").strip()
    if style_prompt and style_prompt.lower() not in prompt.lower():
        prompt = f"{prompt}, {style_prompt}" if prompt else style_prompt

    MIN_LENGTH = 20
    if len(prompt) < MIN_LENGTH:

        prompt += ", masterpiece, ultra-detailed, high quality, 8k resolution, professional lighting"

    prompt = prompt.strip(", ").strip()

    return prompt

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
    prompt = prompt.strip(",. ").strip()

    style_prompt = PROMPT_PRESETS.get(style, "").strip()

    if style_prompt and style_prompt.lower() not in prompt.lower():
        prompt = f"{prompt}, {style_prompt}" if prompt else style_prompt

    MIN_LENGTH = 30
    if len(prompt) < MIN_LENGTH:
        quality_keywords = "masterpiece, ultra-detailed, 8k resolution, high realism"
        if quality_keywords.lower() not in prompt.lower():
            prompt += ", " + quality_keywords

    return prompt.strip(", ").strip()

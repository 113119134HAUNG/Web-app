# prompt_engineering.py

import re
from config import PROMPT_PRESETS
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > 0.85
    
MIN_LENGTH = 30
QUALITY_KEYWORDS = ", ".join(["masterpiece", "ultra-detailed", "8k resolution", "high realism"])

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

    if style_prompt and not any(p.strip().lower() in prompt.lower() for p in style_prompt.split(",")):
        prompt = f"{prompt}, {style_prompt}" if prompt else style_prompt

    if len(prompt) < MIN_LENGTH and QUALITY_KEYWORDS.lower() not in prompt.lower():
        prompt += ", " + QUALITY_KEYWORDS

    return prompt.strip(", ").strip()

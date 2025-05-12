import re
from difflib import SequenceMatcher
from config import PROMPT_PRESETS

# 高品質關鍵詞清單，可擴充
QUALITY_KEYWORDS = [
    "masterpiece", "ultra-detailed", "8k resolution", "high realism"
]
MIN_LENGTH = 30

def similar(a: str, b: str) -> bool:
    """模糊比對兩個句子是否高度相似"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > 0.85

def preprocess_prompt(prompt: str, style: str) -> str:
    if not prompt:
        prompt = ""

    # 標點清理與格式化
    prompt = prompt.replace("，", ",").replace("。", ".")
    prompt = re.sub(r"\s*,\s*", ", ", prompt)
    prompt = re.sub(r"\s*\.\s*", ". ", prompt)
    prompt = re.sub(r"\s{2,}", " ", prompt)
    prompt = prompt.strip(",. ").strip()

    # 使用者輸入轉 set
    prompt_parts = set(p.strip() for p in prompt.split(",") if p.strip())

    # 風格詞彙轉 set 並用 fuzzy 比對過濾與原 prompt 太相似者
    style_prompt = PROMPT_PRESETS.get(style, "")
    if style_prompt:
        style_parts = set(p.strip() for p in style_prompt.split(",") if p.strip())
        filtered_style_parts = {
            sp for sp in style_parts
            if all(not similar(sp, pp) for pp in prompt_parts)
        }
        prompt_parts.update(filtered_style_parts)

    # 若 prompt 長度不足 且未含品質關鍵詞，加入品質提示
    if len(prompt) < MIN_LENGTH and not any(q.lower() in prompt.lower() for q in QUALITY_KEYWORDS):
        prompt_parts.update(QUALITY_KEYWORDS)

    # 組合成乾淨的輸出字串
    return ", ".join(sorted(prompt_parts))
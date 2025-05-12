# rest_prompt.py

import io
import torch
import requests

from PIL import Image
from pathlib import Path
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.responses import Response

from config import DEFAULT_WIDTH, DEFAULT_HEIGHT, NEGATIVE_PROMPT, CACHE_DIR
from cloudflared_runner import get_current_url

app = FastAPI()

# === 安全尺寸限制 ===
def get_safe_dim(value, default):
    try:
        v = int(value)
        return max(64, min(v, 2048))
    except Exception:
        return default

# === API 請求結構定義 ===
class PromptRequest(BaseModel):
    prompt: str
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    seed: int = 42

@app.post("/prompt")
async def generate_image(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "").strip()
        width = get_safe_dim(data.get("width", DEFAULT_WIDTH), DEFAULT_WIDTH)
        height = get_safe_dim(data.get("height", DEFAULT_HEIGHT), DEFAULT_HEIGHT)
        seed = int(data.get("seed", 42))

        if not prompt:
            return {"error": "請提供有效的 prompt 內容"}

        print(f"[API 請求] Prompt: {prompt} | Size: {width}x{height} | Seed: {seed}")

        payload = {
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "width": width,
            "height": height,
            "seed": seed
        }

        # 從 comfy_url.txt 取得目前 ComfyUI URL（支援 cloudflared 公網）
        comfy_api_url = get_current_url(default="http://127.0.0.1:8188")

        # POST 給 ComfyUI REST API
        res = requests.post(f"{comfy_api_url}/prompt", json=payload, timeout=60)
        res.raise_for_status()

        return Response(content=res.content, media_type="image/png")

    except requests.exceptions.Timeout:
        return {"error": "ComfyUI 請求逾時"}

    except requests.exceptions.RequestException as e:
        return {"error": f"ComfyUI 請求錯誤: {str(e)}"}

    except Exception as e:
        print(f"[錯誤] {e}")
        return {"error": f"伺服器錯誤: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8501)
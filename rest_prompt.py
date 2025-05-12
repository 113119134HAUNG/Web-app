# rest_prompt.py

import io
import torch
import uvicorn
import requests

from PIL import Image
from pydantic import BaseModel
from fastapi import FastAPI, Request
from starlette.responses import Response
from config import (
    DEFAULT_WIDTH, DEFAULT_HEIGHT,
    NEGATIVE_PROMPT, CACHE_DIR
)

COMFY_API_URL = "http://127.0.0.1:8188"

app = FastAPI()

# 輔助函式：安全取得寬高，防止異常與過大尺寸
def get_safe_dim(value, default):
    try:
        value = int(value)
        return max(64, min(value, 2048))
    except Exception:
        return default

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

        print(f"[請求] Prompt: {prompt} | Size: {width}x{height} | Seed: {seed}")

        # 準備 ComfyUI 請求 payload
        payload = {
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "width": width,
            "height": height,
            "seed": seed
        }

        # 呼叫 ComfyUI REST API
        res = requests.post(f"{COMFY_API_URL}/prompt", json=payload)
        if res.status_code != 200:
            return {"error": f"ComfyUI 連線失敗 ({res.status_code})"}

        image_bytes = io.BytesIO(res.content)
        return Response(content=image_bytes.read(), media_type="image/png")

    except Exception as e:
        print(f"[錯誤] {e}")
        return {"error": f"伺服器錯誤: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8501)

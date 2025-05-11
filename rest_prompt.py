# rest_prompt.py

import io
import torch
import uvicorn

from PIL import Image
from pydantic import BaseModel
from fastapi import FastAPI, Request
from starlette.responses import Response
from diffusers import StableDiffusionPipeline
from config import (
    MODEL_PATH, CACHE_DIR,
    NEGATIVE_PROMPT, DEFAULT_WIDTH, DEFAULT_HEIGHT
)

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

app = FastAPI()

# 初始化模型
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True,
    cache_dir=CACHE_DIR
).to("cuda")

pipe.safety_checker = None

# 輔助函式：安全取得寬高，防止異常與過大尺寸
def get_safe_dim(value, default):
    try:
        value = int(value)
        return max(64, min(value, 2048))  # 限制 64 ~ 2048
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
            return {"error": "❌ 請提供有效的 prompt 內容"}

        print(f"[請求] Prompt: {prompt} | Size: {width}x{height} | Seed: {seed}")

        generator = torch.Generator("cuda").manual_seed(seed)

        result = pipe(
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            width=width,
            height=height,
            guidance_scale=7.5,
            generator=generator,
            num_inference_steps=30
        )

        image = result.images[0]
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        del result
        torch.cuda.empty_cache()

        return Response(content=image_bytes.read(), media_type="image/png")

    except Exception as e:
        print(f"[錯誤] {e}")
        return {"error": f"❌ 伺服器錯誤：{str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8188)

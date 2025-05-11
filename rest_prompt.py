# rest_prompt.py

import io
import torch

from PIL import Image
from config import MODEL_PATH
from pydantic import BaseModel
from fastapi import FastAPI, Request
from starlette.responses import Response
from diffusers import StableDiffusionPipeline

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 啟動 FastAPI 應用
app = FastAPI()

# 預載入 Stable Diffusion 3 Medium 模型
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
).to("cuda")

pipe.safety_checker = None

class PromptRequest(BaseModel):
    prompt: str
    width: int = 768
    height: int = 768
    seed: int = 42

@app.post("/prompt")
async def generate_image(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "").strip()
        width = int(data.get("width", 768))
        height = int(data.get("height", 768))
        seed = int(data.get("seed", 42))

        if width > 2048 or height > 2048:
            return {"error": "❌ 圖片尺寸過大（最大 2048x2048）"}

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

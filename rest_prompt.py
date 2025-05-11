# rest_prompt.py

import io
import torch
from PIL import Image
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.responses import Response
from diffusers import StableDiffusionPipeline

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

app = FastAPI()

pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium",
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
).to("cuda")

# 關閉安全過濾器
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
        prompt = data.get("prompt", "")
        width = data.get("width", 768)
        height = data.get("height", 768)
        seed = data.get("seed", 42)

        generator = torch.Generator("cuda").manual_seed(seed)

        result = pipe(
            prompt=prompt,
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

        return Response(content=image_bytes.read(), media_type="image/png")

    except Exception as e:
        return {"error": str(e)}

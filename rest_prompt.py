# rest_prompt.py

import io
import torch
import uvicorn

from PIL import Image
from pydantic import BaseModel
from fastapi import FastAPI, Request
from starlette.responses import Response
from diffusers import StableDiffusionPipeline

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 啟動 FastAPI 應用
app = FastAPI()

MODEL_PATH = "models/checkpoints/sd3-medium.safetensors"

# 預載入 Stable Diffusion 3 Medium 模型
pipe = StableDiffusionPipeline.from_single_file(
    pretrained_model_link_or_path=MODEL_PATH,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
).to("cuda")

pipe.safety_checker = None

NEGATIVE_PROMPT = '''(worst quality:1.2), (low quality:1.2), (normal quality:1.2), (lowres:1.1), (low resolution:1.1), blurry, out of focus, depth of field, bokeh,
    pixelated, jpeg artifacts, compression artifacts, grainy, noisy, film grain, underexposed, overexposed, blown highlights, crushed blacks, over-saturation, over-sharpened,
    chromatic aberration, lens flare, lens distortion, vignette, watermark, text, caption, signature, artist name, logo, copyright symbol, branding, border, frame, padding, cropped image,
    duplicate elements, repeating elements, multiple versions, bad anatomy, deformed anatomy, distorted anatomy, disfigured, malformed limbs, missing limbs, floating limbs, disconnected limbs,
    extra limbs, mutated hands, mutilated, poorly drawn hands, poorly drawn face, poorly drawn feet, missing fingers, extra fingers, fused fingers, too many fingers, long neck, cross-eyed,
    crossed eyes, misaligned eyes, asymmetric eyes, heterochromia, deformed iris, blurry iris, bad proportions, unnatural pose, deformed, mutated, twisted body, contorted pose, anatomical nonsense,
    anatomically incorrect, unrealistic proportions, disproportionate body, elongated body parts, incorrect scale, cartoon, 3d render, 3d model, CGI, computer generated, digital art, painting, sketch,
    drawing, anime, manga sketch, cartoon character, illustrated, cell-shaded, line art, flat shading, clip art, artificial, amateur, amateurish, beginner art, hobby art, unprofessional, sloppy, messy,
    scribble, childish, AI-generated, old, outdated, strange colors, unrealistic lighting, poor composition, unrefined, simplistic, stock image, monochrome, grayscale, black and white, sepia, duotone, gaussian blur,
    motion blur, unfocused, soft focus, haze, fog filter, glitch, corrupted image, visual artifacts, rendering errors, aliasing, moire patterns, posterization'''

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8188)

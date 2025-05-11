# comfy_client.py

import requests
import io
from PIL import Image

def generate_with_comfyui(prompt: str, width: int, height: int, seed: int, comfy_api_url: str):

    try:
        response = requests.post(f"{comfy_api_url}/prompt", json={
            "prompt": prompt,
            "width": width,
            "height": height,
            "seed": seed
        })

        if response.status_code == 200:
            image_bytes = response.content
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return image, "（主模型 ComfyUI SD3 成功）"
        else:
            return None, f"主模型失敗：{response.status_code}"
    except Exception as e:
        return None, f"主模型錯誤：{e}"
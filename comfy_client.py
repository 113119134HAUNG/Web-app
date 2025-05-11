# comfy_client.py

import io
import requests
from PIL import Image
from io import BytesIO

def load_comfyui_url(default="http://localhost:8188") -> str:
    try:
        with open("comfy_url.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return default

def generate_with_comfyui(prompt: str, width: int = 512, height: int = 512, seed: int = 42) -> tuple:
    comfy_api_url = load_comfyui_url()

    try:
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "seed": seed
        }
        response = requests.post(f"{comfy_api_url}/prompt", json=payload, timeout=30)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content)).convert("RGB")
        return image, "成功使用主模型 ComfyUI (SD3)"

    except requests.exceptions.Timeout:
        return None, "請求逾時（ComfyUI 未回應）"

    except requests.exceptions.RequestException as e:
        return None, f"主模型錯誤：{e}"

    except Exception as e:
        return None, f"影像處理失敗：{e}"

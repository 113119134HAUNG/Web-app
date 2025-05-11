# comfy_client.py

import io
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path

def load_comfyui_url(default: str = "http://127.0.0.1:8501") -> str:
    url_path = Path("/content/Web-app/comfy_url.txt")
    if url_path.exists():
        try:
            return url_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            print(f"⚠️ 無法讀取 comfy_url.txt，使用預設網址: {e}")
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
        return None, "請求逾時：ComfyUI 沒有回應"

    except requests.exceptions.RequestException as e:
        return None, f"請求錯誤：{e}"

    except Exception as e:
        return None, f"圖像處理錯誤：{e}"

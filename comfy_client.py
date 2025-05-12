# comfy_client.py

import requests
from PIL import Image
from io import BytesIO
from pathlib import Path

COMFY_URL_FILE = Path("/content/Web-app/comfy_url.txt")
DEFAULT_COMFY_URL = "http://127.0.0.1:8188"

def load_comfyui_url(default: str = DEFAULT_COMFY_URL) -> str:
    
    if COMFY_URL_FILE.exists():
        try:
            url = COMFY_URL_FILE.read_text(encoding="utf-8").strip()
            if url.startswith("http"):
                return url
        except Exception as e:
            print(f"無法讀取 comfy_url.txt，使用預設網址: {e}")
    return default

def generate_with_comfyui(prompt: str, width: int = 512, height: int = 512, seed: int = 42) -> tuple[Image.Image | None, str]:
    """
    使用 comfy_url 發送 /prompt API，接收並解碼圖片
    """
    comfy_api_url = load_comfyui_url()
    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "seed": seed
    }

    try:
        response = requests.post(f"{comfy_api_url}/prompt", json=payload, timeout=30)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        return image, f"已使用 ComfyUI 模型推論成功\n📡 API：{comfy_api_url}"

    except requests.exceptions.Timeout:
        return None, f"請求逾時：ComfyUI ({comfy_api_url}) 未回應"

    except requests.exceptions.RequestException as e:
        return None, f"API 請求失敗：{e}"

    except Exception as e:
        return None, f"圖像處理失敗：{e}"

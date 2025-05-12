# comfy_client.py

import requests
from PIL import Image
from io import BytesIO
from pathlib import Path

COMFY_URL_FILE = Path("/content/Web-app/comfy_url.txt")
DEFAULT_COMFY_URL = "http://127.0.0.1:8188"

def load_comfyui_url(default: str = DEFAULT_COMFY_URL) -> str:
    """
    優先從 comfy_url.txt 讀取 URL，如無效或錯誤則返回預設值
    """
    try:
        if COMFY_URL_FILE.exists():
            url = COMFY_URL_FILE.read_text(encoding="utf-8").strip()
            if url.startswith("http"):
                return url
            else:
                print(f"無效的 URL 格式於 comfy_url.txt：{url}")
        else:
            print("未找到 comfy_url.txt，使用預設 localhost")
    except Exception as e:
        print(f"讀取 comfy_url.txt 發生錯誤：{e}")

    return default

def generate_with_comfyui(prompt: str, width: int = 512, height: int = 512, seed: int = 42) -> tuple[Image.Image | None, str]:
    """
    發送 Prompt 至 ComfyUI 的 /prompt API 並回傳圖像
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
        return image, f"成功連線 ComfyUI 模型\n📡 API：{comfy_api_url}"

    except requests.exceptions.Timeout:
        return None, f"逾時：ComfyUI 未於 30 秒內回應 ({comfy_api_url})"

    except requests.exceptions.ConnectionError:
        return None, f"錯誤：無法連線至 ComfyUI API ({comfy_api_url})，請檢查 tunnel 是否存在"

    except requests.exceptions.RequestException as e:
        return None, f"請求錯誤：{e}"

    except Exception as e:
        return None, f"圖像處理錯誤：{e}"
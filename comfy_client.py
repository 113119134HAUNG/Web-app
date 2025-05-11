# comfy_client.py

import io
import requests
from PIL import Image
from io import BytesIO

def generate_with_comfyui(prompt: str, width: int = 512, height: int = 512, seed: int = 42, comfy_api_url: str = "http://localhost:8188"):
    """
    使用 ComfyUI API 呼叫生成圖像。
    回傳 (Image, 狀態訊息)；失敗時 Image 為 None。
    """
    try:
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "seed": seed
        }
        response = requests.post(f"{comfy_api_url}/prompt", json=payload, timeout=30)
        response.raise_for_status()

        image = Image.open(io.BytesIO(response.content)).convert("RGB")
        return image, "✅ 成功使用主模型 ComfyUI (SD3)"

    except requests.exceptions.Timeout:
        return None, "❌ 請求逾時（ComfyUI 未回應）"

    except requests.exceptions.RequestException as e:
        return None, f"❌ 主模型錯誤：{e}"

    except Exception as e:
        return None, f"❌ 影像處理失敗：{e}"

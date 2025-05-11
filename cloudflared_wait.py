# cloudflared_wait.py

import time
import os
import re
from pathlib import Path

def wait_for_cloudflared_log(
    log_path: str = "tunnel.log",
    max_wait_seconds: int = 60,
    output_path: str = "/content/Web-app/comfy_url.txt"
) -> str | None:
    comfy_url = None
    print("正在等待 cloudflared 建立連線...")

    for _ in range(max_wait_seconds // 5):
        time.sleep(5)
        if not os.path.exists(log_path):
            continue
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                logs = f.read()
            urls = re.findall(r"https://.*?trycloudflare.com", logs)
            if urls:
                comfy_url = urls[-1]
                print("ComfyUI 外部網址：", comfy_url)
                Path(output_path).write_text(comfy_url, encoding="utf-8")
                break
        except Exception as e:
            print(f"[錯誤] 讀取或寫入失敗: {e}")
            break

    if not comfy_url:
        print("無法取得 Cloudflared 網址，請檢查 tunnel.log 或 Cloudflared 是否已啟動")

    return comfy_url

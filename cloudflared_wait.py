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

    wait_interval = 2
    max_loops = max_wait_seconds // wait_interval

    for _ in range(max_loops):
        time.sleep(wait_interval)
        if not os.path.exists(log_path):
            continue
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                logs = f.read()

            # 精準抓 cloudflared 公開網址區段
            match = re.search(
                r"https://[a-z0-9-]+\.trycloudflare\.com", logs, re.IGNORECASE
            )
            if match:
                comfy_url = match.group(0)
                print("ComfyUI 外部網址：", comfy_url)
                Path(output_path).write_text(comfy_url, encoding="utf-8")
                break

        except Exception as e:
            print(f"讀取或寫入失敗: {e}")
            break

    if not comfy_url:
        print("⚠️ 無法取得 Cloudflared 網址，請檢查 tunnel.log 或確認 Gradio 是否啟動")

    return comfy_url

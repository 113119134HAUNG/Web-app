# cloudflared_wait.py

import time
import os
import re

def wait_for_cloudflared_log(log_path="tunnel.log", max_wait_seconds=60):
    comfy_url = None

    print("正在等待 cloudflared 建立連線...")

    for _ in range(max_wait_seconds // 5):
        time.sleep(5)
        if not os.path.exists(log_path):
            continue
        with open(log_path, "r") as f:
            logs = f.read()
        urls = re.findall(r"https://.*?trycloudflare.com", logs)
        if urls:
            comfy_url = urls[-1]
            print("ComfyUI 外部網址：", comfy_url)
            with open("comfy_url.txt", "w") as f:
                f.write(comfy_url)
            break

    if not comfy_url:
        print("無法取得 cloudflared 網址，請檢查 tunnel.log 或 cloudflared 是否啟動")

    return comfy_url

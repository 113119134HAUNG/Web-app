# startup.py

import os
import time
import subprocess
from IPython.display import display, Markdown
from cloudflared_wait import wait_for_cloudflared_log

# 清除殘留進程
os.system("pkill -f 'python main.py' || true")
os.system("pkill -f 'cloudflared' || true")
os.system("pkill -f 'uvicorn' || true")

# 啟動 ComfyUI
subprocess.Popen([
    "python", "main.py",
    "--disable-auto-launch",
    "--listen", "127.0.0.1",
    "--port", "8188"
], stdout=open("comfy.log", "w"), stderr=subprocess.STDOUT)

time.sleep(10)

# 啟動 FastAPI
subprocess.Popen([
    "uvicorn", "rest_prompt:app",
    "--host", "127.0.0.1",
    "--port", "8501",
    "--log-level", "warning"
], stdout=open("fastapi.log", "w"), stderr=subprocess.STDOUT)

time.sleep(5)

# 啟動 cloudflared
if not os.path.exists("cloudflared"):
    os.system("wget -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64")
    os.system("chmod +x cloudflared")
os.system("nohup ./cloudflared tunnel --url http://localhost:7860 > tunnel.log 2>&1 &")

time.sleep(8)

# 抓取外部網址
try:
    GRADIO_EXTERNAL_URL = wait_for_cloudflared_log()
    print(f"\nWeb App 已啟動，請開啟：{GRADIO_EXTERNAL_URL}")
if GRADIO_EXTERNAL_URL:
    display(Markdown(f"### 點此開啟 Web UI：[**Gradio 入口**]({GRADIO_EXTERNAL_URL})"))
else:
    print("⚠️ 無法取得外部網址，請手動查看 tunnel.log")

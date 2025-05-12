# startup.py

import os
import time
import socket
import subprocess
import threading
from pathlib import Path
from IPython.display import display, Markdown
from cloudflared_wait import wait_for_cloudflared_log

def wait_for_port(port, host="127.0.0.1", timeout=60, rest_after_ready=2):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                time.sleep(rest_after_ready)
                return True
        except OSError:
            time.sleep(1)
    return False

# 清除残留進程
os.system("pkill -f 'python main.py' || true")
os.system("pkill -f 'cloudflared' || true")
os.system("pkill -f 'uvicorn' || true")

# 啟動 ComfyUI
os.chdir("/content/ComfyUI")
subprocess.Popen([
    "python", "main.py",
    "--disable-auto-launch",
    "--listen", "127.0.0.1",
    "--port", "8188"
], stdout=open("comfy.log", "w"), stderr=subprocess.STDOUT)
wait_for_port(8188)

# 啟動 FastAPI
os.chdir("/content/Web-app")
subprocess.Popen([
    "uvicorn", "rest_prompt:app",
    "--host", "127.0.0.1",
    "--port", "8501",
    "--log-level", "warning"
], stdout=open("fastapi.log", "w"), stderr=subprocess.STDOUT)
wait_for_port(8501)

# 啟動 Gradio Web App
subprocess.Popen(["python", "app.py"])
print("等待 Gradio 啟動...")

def launch_cloudflared_when_ready():
    if wait_for_port(7860, timeout=60):
        print("Gradio 已啟動, 開始 cloudflared 穿透...")
        if not Path("cloudflared").exists():
            raise FileNotFoundError("❌ 找不到 cloudflared，請先在 Colab 初始化區塊下載並授權")
        subprocess.Popen(
            ["./cloudflared", "tunnel", "--url", "http://localhost:7860"],
            stdout=open("tunnel.log", "w"),
            stderr=subprocess.STDOUT
        )
        time.sleep(6)
        try:
            url = wait_for_cloudflared_log()
            print(f"\nWeb App 已啟動，請開啟：{url}")
            display(Markdown(f"### 點此開啟 Web UI：[**Gradio 入口**]({url})"))
        except Exception as e:
            print("無法取得 cloudflared URL，請手動查看 tunnel.log")
            print("Error:", str(e))
    else:
        print("Gradio 啟動連續失敗, cloudflared 未啟動")

# 使用線程背景啟動 cloudflared
threading.Thread(target=launch_cloudflared_when_ready, daemon=True).start()

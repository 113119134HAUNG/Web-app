# startup.py

import os
import time
import socket
import subprocess
from pathlib import Path
from cloudflared_runner import launch_cloudflared_background
from IPython.display import display, Markdown

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

# 清除前次殘留進程
os.system("pkill -f 'python main.py' || true")
os.system("pkill -f 'cloudflared' || true")
os.system("pkill -f 'uvicorn' || true")

# 啟動 ComfyUI
os.chdir("/content/ComfyUI")
subprocess.Popen(["python", "main.py", "--disable-auto-launch", "--listen", "127.0.0.1", "--port", "8188"],
                 stdout=open("comfy.log", "w"), stderr=subprocess.STDOUT)
wait_for_port(8188)

# 啟動 FastAPI
os.chdir("/content/Web-app")
subprocess.Popen(["uvicorn", "rest_prompt:app", "--host", "127.0.0.1", "--port", "8501", "--log-level", "warning"],
                 stdout=open("fastapi.log", "w"), stderr=subprocess.STDOUT)
wait_for_port(8501)

# 啟動 Gradio Web App
subprocess.Popen(["python", "app.py"])
print("等待 Gradio 啟動...")

# 啟動 cloudflared
subprocess.Popen(
    ["./cloudflared", "tunnel", "--url", "http://127.0.0.1:7860"],
    cwd="/content/Web-app",
    stdout=open("/content/Web-app/tunnel.log", "w"),
    stderr=subprocess.STDOUT)

# 解析公開網址
from cloudflared_runner import wait_for_cloudflared_url
wait_for_cloudflared_url()

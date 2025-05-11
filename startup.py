# startup.py

import os
import time
import socket
import subprocess
from IPython.display import display, Markdown
from cloudflared_wait import wait_for_cloudflared_log

# 清除残留進程
os.system("pkill -f 'python main.py' || true")
os.system("pkill -f 'cloudflared' || true")
os.system("pkill -f 'uvicorn' || true")

# 先切換目錄
os.chdir("/content/ComfyUI")

# 啟動 ComfyUI
subprocess.Popen([
    "python", "main.py",
    "--disable-auto-launch",
    "--listen", "127.0.0.1",
    "--port", "8188"
], stdout=open("comfy.log", "w"), stderr=subprocess.STDOUT)

time.sleep(10)

os.chdir("/content/Web-app")

# 啟動 FastAPI
subprocess.Popen([
    "uvicorn", "rest_prompt:app",
    "--host", "127.0.0.1",
    "--port", "8501",
    "--log-level", "debug"
], stdout=open("fastapi.log", "w"), stderr=subprocess.STDOUT)

time.sleep(5)

# 啟動 Gradio Web App
subprocess.Popen(["python", "app.py"])

def wait_for_port(port, timeout=30):
    """ 等待指定 port 啟動 """
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(1)
    return False

print("\u7b49\u5f85 Gradio 啟動...")
if wait_for_port(7860, timeout=40):
    print("Gradio 已啟動, 開始 cloudflared 穿透...")
    if not os.path.exists("cloudflared"):
        os.system("wget -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64")
        os.system("chmod +x cloudflared")
    os.system("nohup ./cloudflared tunnel --url http://localhost:7860 > tunnel.log 2>&1 &")

    time.sleep(6)
    try:
        GRADIO_EXTERNAL_URL = wait_for_cloudflared_log()
        print(f"\nWeb App 已啟動，請開啟：{GRADIO_EXTERNAL_URL}")
        display(Markdown(f"### 點此開啟 Web UI：[**Gradio 入口**]({GRADIO_EXTERNAL_URL})"))
    except Exception as e:
        print("\u26a0\ufe0f 無法取得 cloudflared URL, 請手動查看 tunnel.log")
        print("\u932f誤：", str(e))
else:
    print("Gradio 啟動連續失敗, cloudflared 未啟動")

# cloudflared_runner.py

import subprocess
import threading
import time
import re
from pathlib import Path

# 路徑設定
ROOT_DIR = Path("/content/Web-app")
CLOUDFLARED_BIN = ROOT_DIR / "cloudflared"
TUNNEL_LOG = ROOT_DIR / "tunnel.log"
URL_OUTPUT = ROOT_DIR / "comfy_url.txt"
CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

def download_cloudflared_if_needed():
    if CLOUDFLARED_BIN.exists():
        print("cloudflared 已存在，略過下載")
        return
    print("正在下載 cloudflared...")
    subprocess.run(["wget", "-O", str(CLOUDFLARED_BIN), CLOUDFLARED_URL], check=True)
    subprocess.run(["chmod", "+x", str(CLOUDFLARED_BIN)], check=True)
    print("cloudflared 已下載並設為可執行")

def wait_for_url_from_log(timeout=60) -> str | None:
    """從 tunnel.log 監聽網址並寫入 comfy_url.txt"""
    for _ in range(timeout):
        if TUNNEL_LOG.exists():
            try:
                text = TUNNEL_LOG.read_text(encoding="utf-8", errors="ignore")
                match = re.findall(r"https://[^\s]+?\.trycloudflare\.com", text)
                if match:
                    url = match[-1]
                    URL_OUTPUT.write_text(url, encoding="utf-8")
                    print(f"公開網址已取得：{url}")
                    return url
            except Exception as e:
                print(f"無法讀取 tunnel.log：{e}")
        time.sleep(1)
    print("未能取得 cloudflared 公開網址")
    return None

def launch_cloudflared_background(port: int = 7860):
    """啟動 cloudflared 並背景監聽網址"""
    def _run():
        try:
            download_cloudflared_if_needed()
            print(f"啟動 cloudflared（連接至 http://localhost:{port}）")
            subprocess.Popen(
                [f"./{CLOUDFLARED_BIN.name}", "tunnel", "--url", f"http://localhost:{port}"],
                cwd=ROOT_DIR,
                stdout=TUNNEL_LOG.open("w"),
                stderr=subprocess.STDOUT
            )
            wait_for_url_from_log()
        except Exception as e:
            print(f"cloudflared 啟動錯誤：{e}")
    threading.Thread(target=_run, daemon=True).start()

def get_current_url(default="http://127.0.0.1:8188") -> str:
    """讀取 comfy_url.txt 的公開網址"""
    if URL_OUTPUT.exists():
        try:
            return URL_OUTPUT.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return default

# CLI 測試支援
if __name__ == "__main__":
    launch_cloudflared_background(port=7860)
    print("正在背景啟動 cloudflared...")
    time.sleep(10)
    print("取得網址：", get_current_url())

# cloudflared_runner.py

import time
import re
from pathlib import Path

# 設定統一目錄與檔案路徑
ROOT_DIR = Path("/content/Web-app")
TUNNEL_LOG = ROOT_DIR / "tunnel.log"
URL_OUTPUT = ROOT_DIR / "comfy_url.txt"
'''def wait_for_cloudflared_url(log_path: Path = TUNNEL_LOG,
                             output_path: Path = URL_OUTPUT,
                             max_wait_seconds: int = 60) -> str | None:
    
    print("正在監聽 cloudflared log，等待公開網址產生...")

    wait_interval = 2
    max_loops = max_wait_seconds // wait_interval

    for _ in range(max_loops):
        time.sleep(wait_interval)
        if not log_path.exists():
            continue
        try:
            logs = log_path.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", logs, re.IGNORECASE)
            if match:
                url = match.group(0)
                output_path.write_text(url.strip(), encoding="utf-8")
                print(f"公開網址擷取成功並已儲存：{url}")
                return url
        except Exception as e:
            print(f"❌ 解析 cloudflared 日誌時發生錯誤：{e}")
            break

    print("⚠️ 未能取得公開網址，請確認 cloudflared 是否已正常啟動")
    return None'''


def get_current_url(default: str = "http://127.0.0.1:8188") -> str:

    try:
        if URL_OUTPUT.exists():
            return URL_OUTPUT.read_text(encoding="utf-8").strip()
    except Exception as e:
        print(f"⚠️ 讀取 comfy_url.txt 失敗：{e}")
    return default

def write_url_to_file(url: str) -> None:
    
    try:
        URL_OUTPUT.write_text(url.strip(), encoding="utf-8")
        print(f"公開網址已寫入 comfy_url.txt：{url}")
    except Exception as e:
        print(f"寫入 comfy_url.txt 失敗：{e}")


# 測試 CLI（可選）
if __name__ == "__main__":
    url = wait_for_cloudflared_url()
    print("擷取網址結果：", url or get_current_url())

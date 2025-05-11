# stats.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os
from config import PROMPT_LOG_PATH

matplotlib.rcParams['font.family'] = 'Noto Sans CJK TC'  # 可替換成 'Taipei Sans TC Beta', 'Microsoft JhengHei' 等系統字型

def load_log_df():
    if not os.path.exists(PROMPT_LOG_PATH):
        return pd.DataFrame(columns=["time", "prompt", "style"])
    try:
        df = pd.read_csv(PROMPT_LOG_PATH, names=["time", "prompt", "style"])
        return df
    except Exception as e:
        print(f"❌ 載入紀錄檔失敗: {e}")
        return pd.DataFrame(columns=["time", "prompt", "style"])

def plot_prompt_usage(df):
    try:
        if df.empty or "style" not in df:
            raise ValueError("無可用的風格資料")
        top_styles = df["style"].value_counts().head(5)
        fig, ax = plt.subplots()
        top_styles.plot(kind="bar", ax=ax, title="最常用風格", color="skyblue")
        ax.set_ylabel("次數")
        ax.set_xlabel("風格")
        plt.tight_layout()
        return fig
    except Exception as e:
        print(f"❌ 畫圖失敗（風格統計）: {e}")
        return error_figure(str(e))

def plot_time_distribution(df):
    try:
        if df.empty or "time" not in df:
            raise ValueError("無時間資料")
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])
        if df.empty:
            raise ValueError("無有效時間紀錄")
        df["hour"] = df["time"].dt.hour
        fig, ax = plt.subplots()
        df["hour"].value_counts().sort_index().plot(kind="bar", ax=ax, title="按小時使用分佈", color="orange")
        ax.set_ylabel("次數")
        ax.set_xlabel("小時")
        plt.tight_layout()
        return fig
    except Exception as e:
        print(f"❌ 畫圖失敗（時間統計）: {e}")
        return error_figure(str(e))

def error_figure(msg: str):
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, f"錯誤：{msg}", fontsize=12, ha='center', va='center', color='red')
    ax.axis('off')
    return fig

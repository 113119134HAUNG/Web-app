# stats.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from config import PROMPT_LOG_PATH

matplotlib.rcParams['font.family'] = [
    'Noto Sans CJK TC', 'Taipei Sans TC Beta', 'Microsoft JhengHei', 'PingFang TC', 'Arial', 'DejaVu Sans'
]

COL_TIME = "time"
COL_PROMPT = "prompt"
COL_STYLE = "style"

def load_log_df():
    if not os.path.exists(PROMPT_LOG_PATH):
        return pd.DataFrame(columns=[COL_TIME, COL_PROMPT, COL_STYLE])
    try:
        df = pd.read_csv(PROMPT_LOG_PATH, names=[COL_TIME, COL_PROMPT, COL_STYLE])
        return df
    except Exception as e:
        print(f"❌ 無法讀取紀錄檔: {e}")
        return pd.DataFrame(columns=[COL_TIME, COL_PROMPT, COL_STYLE])

def plot_prompt_usage(df):
    try:
        if df.empty or COL_STYLE not in df:
            raise ValueError("缺少風格資料")
        top_styles = df[COL_STYLE].value_counts().head(5)
        fig, ax = plt.subplots()
        top_styles.plot(kind="bar", ax=ax, title="最常使用的風格", color="skyblue")
        ax.set_ylabel("次數")
        ax.set_xlabel("風格")
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    except Exception as e:
        print(f"❌ 繪製風格統計失敗: {e}")
        return error_figure(str(e))

def plot_time_distribution(df):
    try:
        if df.empty or COL_TIME not in df:
            raise ValueError("缺少時間資料")
        df[COL_TIME] = pd.to_datetime(df[COL_TIME], errors="coerce")
        df = df.dropna(subset=[COL_TIME])
        if df.empty:
            raise ValueError("無有效時間紀錄")
        df["hour"] = df[COL_TIME].dt.hour
        hourly = df["hour"].value_counts().sort_index()
        fig, ax = plt.subplots()
        hourly.plot(kind="bar", ax=ax, title="一天中使用高峰", color="orange")
        ax.set_ylabel("次數")
        ax.set_xlabel("小時")
        plt.xticks(rotation=0)
        plt.tight_layout()
        return fig
    except Exception as e:
        print(f"❌ 繪製時間分佈失敗: {e}")
        return error_figure(str(e))

def error_figure(msg: str):
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, f"錯誤：{msg}", fontsize=12, ha='center', va='center', color='red')
    ax.axis('off')
    return fig

if __name__ == "__main__":
    df = load_log_df()
    fig1 = plot_prompt_usage(df)
    fig2 = plot_time_distribution(df)

# stats.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os
from config import PROMPT_LOG_PATH

matplotlib.rcParams['font.family'] = 'DejaVu Sans'  # Or 'Arial', 'Liberation Sans', etc.

def load_log_df():
    if not os.path.exists(PROMPT_LOG_PATH):
        return pd.DataFrame(columns=["time", "prompt", "style"])
    try:
        df = pd.read_csv(PROMPT_LOG_PATH, names=["time", "prompt", "style"])
        return df
    except Exception as e:
        print(f"❌ Failed to load log file: {e}")
        return pd.DataFrame(columns=["time", "prompt", "style"])

def plot_prompt_usage(df):
    try:
        if df.empty or "style" not in df:
            raise ValueError("No available style data.")
        top_styles = df["style"].value_counts().head(5)
        fig, ax = plt.subplots()
        top_styles.plot(kind="bar", ax=ax, title="Top Prompt Styles", color="skyblue")
        ax.set_ylabel("Count")
        ax.set_xlabel("Style")
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    except Exception as e:
        print(f"❌ Failed to plot style usage: {e}")
        return error_figure(str(e))

def plot_time_distribution(df):
    try:
        if df.empty or "time" not in df:
            raise ValueError("No time data available.")
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])
        if df.empty:
            raise ValueError("No valid time records found.")
        df["hour"] = df["time"].dt.hour
        hourly = df["hour"].value_counts().sort_index()
        fig, ax = plt.subplots()
        hourly.plot(kind="bar", ax=ax, title="Usage Distribution by Hour", color="orange")
        ax.set_ylabel("Count")
        ax.set_xlabel("Hour of Day")
        plt.xticks(rotation=0)
        plt.tight_layout()
        return fig
    except Exception as e:
        print(f"❌ Failed to plot time distribution: {e}")
        return error_figure(str(e))

def error_figure(msg: str):
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, f"Error: {msg}", fontsize=12, ha='center', va='center', color='red')
    ax.axis('off')
    return fig


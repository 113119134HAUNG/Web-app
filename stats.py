# stats.py

import pandas as pd
import matplotlib.pyplot as plt
import os
from config import PROMPT_LOG_PATH

def load_log_df():
    if not os.path.exists(PROMPT_LOG_PATH):
        return pd.DataFrame(columns=["time", "prompt", "style"])
    df = pd.read_csv(PROMPT_LOG_PATH, names=["time", "prompt", "style"])
    return df

def plot_prompt_usage(df):
    top_styles = df["style"].value_counts().head(5)
    fig, ax = plt.subplots()
    top_styles.plot(kind="bar", ax=ax, title="最常用風格")
    return fig

def plot_time_distribution(df):
    df["time"] = pd.to_datetime(df["time"])
    df["hour"] = df["time"].dt.hour
    fig, ax = plt.subplots()
    df["hour"].value_counts().sort_index().plot(kind="bar", ax=ax, title="按小時使用分佈")
    return fig

"""
video_maker.py
Compatible with:
- Python 3.14
- moviepy 2.x
- pillow 11.x
"""

import os
import yfinance as yf
import matplotlib.pyplot as plt

from moviepy import (
    ImageClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    ColorClip
)

# -----------------------------
# CONFIG
# -----------------------------
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 24
DEFAULT_DURATION = 30  # seconds


# -----------------------------
# CHART CREATION
# -----------------------------
def create_chart(ticker: str, filename: str) -> str:
    """
    Creates a clean dark-themed chart image for Shorts background
    """
    data = yf.download(
        ticker,
        period="5d",
        interval="15m",
        progress=False
    )

    if data.empty:
        raise ValueError("No data received from Yahoo Finance")

    close = data["Close"]
    if hasattr(close, "columns"):
        close = close.iloc[:, 0]

    close = close.ffill()

    last_price = float(close.iloc[-1])
    first_price = float(close.iloc[0])
    pct_change = ((last_price - first_price) / first_price) * 100

    plt.style.use("dark_background")
    plt.figure(figsize=(6, 10))

    plt.plot(close, linewidth=2)
    plt.axhline(last_price, linestyle="--", alpha=0.8)

    plt.title(
        f"{ticker.replace('^', '')}\n"
        f"Last: {last_price:.2f} | {pct_change:+.2f}%",
        fontsize=18,
        pad=20
    )

    plt.xticks([])
    plt.ylabel("Price")
    plt.grid(alpha=0.3)

    os.makedirs("assets", exist_ok=True)
    path = os.path.join("assets", filename)

    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()

    return path


# -----------------------------
# VIDEO CREATION
# -----------------------------
def create_video(
    chart_path: str,
    audio_path: str,
    output_name: str,
    title_text: str = "NIFTY\nMARKET REPORT"
) -> str:
    """
    Creates a vertical YouTube Shorts video with:
    - Chart background
    - Synced audio
    - Title
    - Disclaimer
    """

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", output_name)

    # -----------------------------
    # AUDIO (SAFE)
    # -----------------------------
    audio = AudioFileClip(audio_path)
    duration = min(audio.duration, DEFAULT_DURATION)

    # -----------------------------
    # BACKGROUND IMAGE
    # -----------------------------
    background = (
        ImageClip(chart_path)
        .resized(height=VIDEO_HEIGHT)
        .with_duration(duration)
        .with_audio(audio)
    )

    # -----------------------------
    # TITLE
    # -----------------------------
    title = (
        TextClip(
            text=title_text,
            font_size=68,
            color="white",
            method="caption",
            size=(1000, None)
        )
        .with_position(("center", 160))
        .with_duration(5)
    )

    # -----------------------------
    # DISCLAIMER STRIP
    # -----------------------------
    disclaimer_bg = (
        ColorClip(
            size=(VIDEO_WIDTH, 120),
            color=(0, 0, 0)
        )
        .with_opacity(0.65)
        .with_position(("center", VIDEO_HEIGHT - 140))
        .with_duration(duration)
    )

    disclaimer_text = (
        TextClip(
            text="For educational purposes only.\nNot investment advice.",
            font_size=30,
            color="white",
            method="caption",
            size=(980, None)
        )
        .with_position(("center", VIDEO_HEIGHT - 130))
        .with_duration(duration)
    )

    # -----------------------------
    # COMPOSE
    # -----------------------------
    final_video = CompositeVideoClip(
        [background, title, disclaimer_bg, disclaimer_text],
        size=(VIDEO_WIDTH, VIDEO_HEIGHT)
    )

    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium"
    )

    return output_path


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    chart = create_chart("^NSEI", "nifty_test.png")
    video = create_video(
        chart_path=chart,
        audio_path="output/postmarket.mp3",
        output_name="test_video.mp4"
    )
    print("Video created:", video)

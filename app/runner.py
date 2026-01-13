"""
runner.py
Main orchestrator for Market Bot
"""

import datetime
import pytz

from data_fetcher import fetch_index_daily
from summarizer import (
    create_premarket_script,
    create_postmarket_script,
    create_weekly_script
)
from tts_adapter import text_to_speech
from video_maker import create_chart, create_video
from youtube_uploader import upload_video


IST = pytz.timezone("Asia/Kolkata")


# -----------------------------
# HELPERS
# -----------------------------
def now_ist():
    return datetime.datetime.now(IST)


def is_sunday():
    return now_ist().weekday() == 6


def current_hour():
    return now_ist().hour


def safe_audio(script: str, filename: str) -> str:
    """
    Ensures audio always exists.
    If Polly fails, creates a silent placeholder MP3.
    """
    audio = text_to_speech(script, filename)
    if audio:
        return audio

    # 🔇 Silent fallback (moviepy can still render)
    print("⚠️ Polly not configured. Using silent audio.")
    import os
    from moviepy import AudioClip

    os.makedirs("output", exist_ok=True)
    path = f"output/{filename}"

    silent = AudioClip(lambda t: 0, duration=30)
    silent.write_audiofile(path, fps=44100)

    return path


# -----------------------------
# REPORT RUNNERS
# -----------------------------
def run_premarket():
    print("Running PREMARKET report")

    nifty = fetch_index_daily("^NSEI")

    global_cues = {
        "us_markets": "Mixed",
        "asia": "Cautious",
        "crude": "Stable",
        "usd_inr": "Range-bound"
    }

    derivatives = {
        "pcr": None,
        "vix": None,
        "oi_trend": None,
        "max_pain": None
    }

    script = create_premarket_script(
        nifty=nifty,
        global_cues=global_cues,
        derivatives=derivatives
    )

    audio = safe_audio(script, "premarket.mp3")
    chart = create_chart("^NSEI", "nifty_premarket.png")

    video = create_video(
        chart_path=chart,
        audio_path=audio,
        output_name="premarket.mp4",
        title_text="NIFTY\nPRE-MARKET REPORT"
    )

    upload_video(
        file_path=video,
        title="Premarket Report | Nifty",
        description="Educational purposes only. Not investment advice.",
        tags=["Nifty", "Premarket", "Stock Market", "Shorts"]
    )


def run_postmarket():
    print("Running POST-MARKET report")

    nifty = fetch_index_daily("^NSEI")

    sectors = {
        "gainers": ["IT", "Pharma"],
        "losers": ["FMCG", "Metal"],
        "rotation": "Selective buying",
        "breadth": "Neutral"
    }

    derivatives = {
        "pcr": None,
        "vix": None,
        "oi_trend": None,
        "max_pain": None
    }

    script = create_postmarket_script(
        nifty=nifty,
        sectors=sectors,
        derivatives=derivatives
    )

    audio = safe_audio(script, "postmarket.mp3")
    chart = create_chart("^NSEI", "nifty_postmarket.png")

    video = create_video(
        chart_path=chart,
        audio_path=audio,
        output_name="postmarket.mp4",
        title_text="NIFTY\nPOST-MARKET REPORT"
    )

    upload_video(
        file_path=video,
        title="Post Market Report | Nifty",
        description="Educational purposes only. Not investment advice.",
        tags=["Nifty", "Post Market", "Stock Market", "Shorts"]
    )


def run_weekly():
    print("Running WEEKLY report")

    weekly_index = fetch_index_daily("^NSEI")

    sectors = {
        "leaders": ["IT", "Banking"],
        "laggards": ["Metal"]
    }

    macro = {
        "inflation": "Stable",
        "rates": "Unchanged",
        "global": "Mixed"
    }

    derivatives = {
        "vix_trend": "Low volatility"
    }

    script = create_weekly_script(
        weekly_index=weekly_index,
        sectors=sectors,
        macro=macro,
        derivatives=derivatives
    )

    audio = safe_audio(script, "weekly.mp3")
    chart = create_chart("^NSEI", "nifty_weekly.png")

    video = create_video(
        chart_path=chart,
        audio_path=audio,
        output_name="weekly.mp4",
        title_text="NIFTY\nWEEKLY ANALYSIS"
    )

    upload_video(
        file_path=video,
        title="Weekly Market Analysis | Nifty",
        description="Educational purposes only. Not investment advice.",
        tags=["Nifty", "Weekly Analysis", "Stock Market"]
    )


# -----------------------------
# ENTRY POINT
# -----------------------------
def main():
    now = now_ist()
    print("Current IST time:", now)

    # Saturday
    if now.weekday() == 5:
        print("Saturday: No report")
        return

    # Sunday
    if is_sunday():
        run_weekly()
        return

    # Weekdays
    if current_hour() < 12:
        run_premarket()
    else:
        run_postmarket()


if __name__ == "__main__":
    main()

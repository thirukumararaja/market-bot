"""
runner.py
Railway-safe version (SCRIPT ONLY)
- No video
- No moviepy
- No YouTube upload
"""

import datetime
import pytz

from data_fetcher import fetch_index_daily
from summarizer import (
    create_premarket_script,
    create_postmarket_script,
    create_weekly_script
)

IST = pytz.timezone("Asia/Kolkata")


# -----------------------------
# TIME HELPERS
# -----------------------------
def now_ist():
    return datetime.datetime.now(IST)


def is_sunday():
    return now_ist().weekday() == 6


def current_hour():
    return now_ist().hour


# -----------------------------
# REPORT RUNNERS (TEXT ONLY)
# -----------------------------
def run_premarket():
    print("🟢 PRE-MARKET SCRIPT")

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

    print("\n--- PREMARKET SCRIPT ---\n")
    print(script)
    print("\n------------------------\n")


def run_postmarket():
    print("🔵 POST-MARKET SCRIPT")

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

    print("\n--- POSTMARKET SCRIPT ---\n")
    print(script)
    print("\n-------------------------\n")


def run_weekly():
    print("🟣 WEEKLY SCRIPT")

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

    print("\n--- WEEKLY SCRIPT ---\n")
    print(script)
    print("\n---------------------\n")


# -----------------------------
# ENTRY POINT
# -----------------------------
def main():
    now = now_ist()
    print("⏰ Current IST:", now)

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

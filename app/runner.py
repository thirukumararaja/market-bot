"""
runner.py - Railway-ready version

Auto-selects task based on IST time:
- Premarket: Mon–Fri 8:00 AM
- Postmarket: Mon–Fri 6:00 PM
- Weekly: Sunday 10:00 AM

Generates script → TTS → Video → Upload to YouTube
Logs everything in console for Railway

Requires environment variables:
- OPENAI_API_KEY
- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- YOUTUBE_REFRESH_TOKEN
"""

import os
from datetime import datetime
import pytz
from summarizer import create_premarket_script, create_postmarket_script, create_weekly_script
from video_maker import create_video_from_script
from utils import fetch_market_data, fetch_global_data, fetch_sectors, fetch_derivatives

# -----------------------------
# TIME & TASK SELECTION
# -----------------------------
IST = pytz.timezone("Asia/Kolkata")
now = datetime.now(IST)
hour = now.hour
weekday = now.weekday()  # Monday=0, Sunday=6

# Decide task
if weekday <= 4:  # Monday–Friday
    if hour == 8:
        TASK = "premarket"
    elif hour == 18:
        TASK = "postmarket"
    else:
        TASK = None
elif weekday == 6:  # Sunday
    if hour == 10:
        TASK = "weekly"
    else:
        TASK = None
else:
    TASK = None

if TASK is None:
    print(f"[{now}] No task scheduled at this time. Exiting.")
    exit(0)

print(f"[{now}] Running task: {TASK.upper()}")

# -----------------------------
# FETCH DATA
# -----------------------------
print("Fetching market & global data...")
nifty_data = fetch_market_data("NIFTY")
banknifty_data = fetch_market_data("BANKNIFTY")
global_data = fetch_global_data()
sectors_data = fetch_sectors()
derivatives_data = fetch_derivatives()

# -----------------------------
# GENERATE SCRIPT
# -----------------------------
script_text = ""
if TASK == "premarket":
    script_text = create_premarket_script(
        nifty=nifty_data,
        global_cues=global_data,
        derivatives=derivatives_data,
        news="Global markets update"
    )
elif TASK == "postmarket":
    script_text = create_postmarket_script(
        nifty=nifty_data,
        sectors=sectors_data,
        derivatives=derivatives_data,
        global_ref=global_data
    )
elif TASK == "weekly":
    script_text = create_weekly_script(
        weekly_index=nifty_data,
        sectors=sectors_data,
        macro=global_data,
        derivatives=derivatives_data
    )

print(f"Script generated ({len(script_text.split())} words).")

# -----------------------------
# CREATE VIDEO
# -----------------------------
output_file = f"output/{TASK}_{now.strftime('%Y%m%d_%H%M')}.mp4"
print(f"Creating video: {output_file}")
create_video_from_script(script_text, output_file)
print("Video created successfully.")

# -----------------------------
# UPLOAD TO YOUTUBE
# -----------------------------
print("Uploading video to YouTube...")
from youtube_uploader import upload_video  # your existing uploader
title_map = {
    "premarket": f"Premarket Report - {now.strftime('%d %b %Y')}",
    "postmarket": f"Postmarket Report - {now.strftime('%d %b %Y')}",
    "weekly": f"Weekly Market Report - Week of {now.strftime('%d %b %Y')}"
}
description_map = {
    "premarket": "Indian stock market premarket analysis. #Nifty #BankNifty #StockMarket",
    "postmarket": "Indian stock market postmarket analysis. #Nifty #BankNifty #StockMarket",
    "weekly": "Weekly market analysis and outlook. #Nifty #BankNifty #StockMarket"
}

upload_video(
    file_path=output_file,
    title=title_map[TASK],
    description=description_map[TASK]
)
print(f"[{now}] Video uploaded successfully!")

print(f"[{now}] Task {TASK.upper()} completed.")

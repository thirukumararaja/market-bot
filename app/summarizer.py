"""
summarizer.py

Generates professional Indian stock market scripts for:
- Premarket (hybrid, forward-looking)
- Postmarket (factual + sector analysis)
- Weekly (detailed thematic)

Features:
- Data-driven + AI-assisted logic
- SEBI-style disclaimer
- YouTube voice-over friendly
- Safe fallbacks if OpenAI fails
"""

from typing import Dict, List, Optional
from openai import OpenAI
from utils import get_env


# -------------------------------------------------
# OPENAI SETUP
# -------------------------------------------------
OPENAI_KEY = get_env("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None


# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
SEBI_DISCLAIMER = (
    "This content is for educational purposes only. "
    "Markets are subject to risk. Please consult your financial advisor "
    "before taking any investment decisions."
)

PREMARKET_MAX_WORDS = 380   # ~2m45s voice-over
POSTMARKET_MAX_WORDS = 380
WEEKLY_MAX_WORDS = 800


# -------------------------------------------------
# HELPER FORMATTERS
# -------------------------------------------------
def _idx_summary(d: Dict) -> str:
    try:
        close = d["close"]
        prev = d["prev_close"]
        high = d.get("high")
        low = d.get("low")
        pct = ((close - prev) / prev) * 100 if prev else 0
        return (
            f"{d.get('symbol','Index')} closed at {close:.2f}, "
            f"up {pct:.2f}%. Day range was {low:.2f}–{high:.2f}."
        )
    except Exception:
        return "Index data was mixed with limited clarity."


def _safe_join(items: Optional[List[str]]) -> str:
    return ", ".join(items) if items else "data not available"


def _derivatives_summary(d: Dict) -> str:
    parts = []
    if d.get("pcr") is not None:
        parts.append(f"PCR at {d['pcr']}")
    if d.get("vix") is not None:
        parts.append(f"India VIX near {d['vix']}")
    if d.get("oi_trend"):
        parts.append(f"OI indicates {d['oi_trend']}")
    if d.get("max_pain"):
        parts.append(f"Max pain around {d['max_pain']}")
    return ", ".join(parts) if parts else "derivatives data was neutral"


# -------------------------------------------------
# FALLBACK SCRIPTS (SAFE MODE)
# -------------------------------------------------
def _fallback_premarket(nifty: Dict) -> str:
    return (
        "Indian markets are set to open today amid mixed global cues. "
        f"{_idx_summary(nifty)} "
        "Derivatives positioning suggests a cautious start. "
        "Traders should watch global markets, crude oil, and key news events. "
        + SEBI_DISCLAIMER
    )


def _fallback_postmarket(nifty: Dict, sectors: Dict) -> str:
    return (
        "Indian markets ended the session on a mixed note. "
        f"{_idx_summary(nifty)} "
        f"Sectoral action was seen in {_safe_join(sectors.get('gainers'))}, "
        f"while pressure was visible in {_safe_join(sectors.get('losers'))}. "
        + SEBI_DISCLAIMER
    )


def _fallback_weekly() -> str:
    return (
        "Indian equity markets concluded the week with selective participation. "
        "Index trends remained range-bound as global and domestic factors influenced sentiment. "
        "Sector rotation and volatility trends will be key to watch next week. "
        + SEBI_DISCLAIMER
    )


# -------------------------------------------------
# PREMARKET SCRIPT (HYBRID)
# -------------------------------------------------
def create_premarket_script(
    nifty: Dict,
    global_cues: Dict,
    derivatives: Dict,
    news: Optional[str] = None
) -> str:

    if not client:
        return _fallback_premarket(nifty)

    prompt = f"""
Create a professional Indian stock market PREMARKET script
for a YouTube voice-over (max {PREMARKET_MAX_WORDS} words).

DATA:
Index data: {nifty}
Global cues: {global_cues}
Derivatives: {derivatives}
News: {news}

TASK:
- Interpret data to infer opening sentiment
- Provide trend bias (bullish / bearish / range-bound)
- Project intraday support and resistance (clearly as expectations)
- Mention key global and macro drivers
- NO buy/sell calls
- Use cautious language like "likely", "expected"
- End with SEBI-style disclaimer
"""

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional Indian market analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.35,
            max_tokens=PREMARKET_MAX_WORDS,
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return _fallback_premarket(nifty)


# -------------------------------------------------
# POSTMARKET SCRIPT
# -------------------------------------------------
def create_postmarket_script(
    nifty: Dict,
    sectors: Dict,
    derivatives: Dict,
    global_ref: Optional[str] = None
) -> str:

    if not client:
        return _fallback_postmarket(nifty, sectors)

    prompt = f"""
Create a factual Indian stock market POSTMARKET script
for a YouTube voice-over (max {POSTMARKET_MAX_WORDS} words).

DATA:
Index data: {nifty}
Sector data: {sectors}
Derivatives: {derivatives}
Global reference: {global_ref}

TASK:
- Summarize index performance
- Mention sector gainers and losers
- Explain sector rotation and market breadth
- Briefly reference derivatives and global cues
- End with SEBI-style disclaimer
"""

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional Indian market analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=POSTMARKET_MAX_WORDS,
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return _fallback_postmarket(nifty, sectors)


# -------------------------------------------------
# WEEKLY SCRIPT (DETAILED)
# -------------------------------------------------
def create_weekly_script(
    weekly_index: Dict,
    sectors: Dict,
    macro: Dict,
    derivatives: Dict
) -> str:

    if not client:
        return _fallback_weekly()

    prompt = f"""
Create a DETAILED weekly Indian stock market analysis
for a YouTube video (max {WEEKLY_MAX_WORDS} words).

DATA:
Weekly index data: {weekly_index}
Sector performance: {sectors}
Macro drivers: {macro}
Derivatives & VIX trend: {derivatives}

TASK:
- Explain weekly index trend
- Highlight leading and lagging sectors
- Describe sector rotation theme
- Cover global and domestic macro drivers
- Discuss derivatives and volatility trend
- Provide cautious outlook for next week
- End with SEBI-style disclaimer
"""

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional Indian market analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.35,
            max_tokens=WEEKLY_MAX_WORDS,
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return _fallback_weekly()


# -------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------
if __name__ == "__main__":
    nifty = {
        "symbol": "NIFTY 50",
        "close": 22500,
        "prev_close": 22380,
        "high": 22620,
        "low": 22310
    }

    sectors = {
        "gainers": ["IT", "Pharma"],
        "losers": ["FMCG", "Metal"],
        "rotation": "Buying in IT and Pharma, profit booking in FMCG",
        "breadth": "Broad-based buying"
    }

    derivatives = {
        "pcr": 1.05,
        "vix": 13.8,
        "oi_trend": "long buildup",
        "max_pain": 22400
    }

    global_cues = {
        "us_markets": "Mixed",
        "asia": "Weak",
        "crude": "Stable",
        "usd_inr": "Slightly higher"
    }

    print("\nPREMARKET:\n", create_premarket_script(nifty, global_cues, derivatives, "Global markets cautious"))
    print("\nPOSTMARKET:\n", create_postmarket_script(nifty, sectors, derivatives))
    print("\nWEEKLY:\n", create_weekly_script(nifty, sectors, global_cues, derivatives))

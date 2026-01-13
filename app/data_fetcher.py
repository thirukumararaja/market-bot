"""
data_fetcher.py

Safe wrapper around yfinance to fetch index daily data.
Returns a dict with keys:
  - symbol
  - close (float or None)
  - prev_close (float or None)
  - error (optional str) when something goes wrong
"""
from typing import Dict, Any
import yfinance as yf


def fetch_index_daily(ticker: str) -> Dict[str, Any]:
    """
    Fetches daily close and previous close for a ticker.

    Returns a dictionary with numeric values or None if unavailable.
    """
    try:
        t = yf.Ticker(ticker)
        # Try 3 days to be safer around market holidays / weekends
        hist = t.history(period="3d", interval="1d")

        if hist is None or len(hist) == 0:
            return {
                "symbol": ticker,
                "close": None,
                "prev_close": None,
                "error": "No historical data returned"
            }

        # Ensure we have at least last row
        last = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) >= 2 else last

        return {
            "symbol": ticker,
            "close": float(last["Close"]) if "Close" in last and not last["Close"] is None else None,
            "prev_close": float(prev["Close"]) if "Close" in prev and not prev["Close"] is None else None
        }

    except Exception as e:
        return {
            "symbol": ticker,
            "close": None,
            "prev_close": None,
            "error": f"Exception fetching data: {e}"
        }


# Standalone test
if __name__ == "__main__":
    print(fetch_index_daily("^NSEI"))
    print(fetch_index_daily("^NSEBANK"))
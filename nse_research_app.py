#!/usr/bin/env python3
"""
Simple NSE Stock App (minimal)
1) Load all NSE symbols (EQ)
2) Search & pick one
3) Show live LTP (NSE) + 6-month line chart (Yahoo)
4) Optional: show promoter holding trend for that stock
"""

import io
import sys
import re
from datetime import datetime
from typing import Optional

import requests
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import pytz

# --- basic settings ---
TZ = pytz.timezone("Asia/Kolkata")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15")

SYMBOL_CSV_URLS = [
    "https://archives.nseindia.com/content/equities/EQUITY_L.csv",
    "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
]

# ----------
# Small helpers
# ----------

def fetch_symbol_master(timeout=20) -> pd.DataFrame:
    """Download official NSE list and keep only Active EQ series."""
    headers = {"User-Agent": UA, "Accept": "text/csv,*/*;q=0.9", "Referer": "https://www.nseindia.com/"}
    last_err = None
    for url in SYMBOL_CSV_URLS:
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(r.content))
            # normalize
            df.columns = [c.strip().upper().replace("  ", " ") for c in df.columns]
            if "SERIES" in df.columns:
                df = df[df["SERIES"].astype(str).str.strip() == "EQ"]
            if "STATUS" in df.columns:
                df = df[df["STATUS"].astype(str).str.upper().str.strip() == "ACTIVE"]
            keep = [c for c in ["SYMBOL", "NAME OF COMPANY", "ISIN NUMBER", "SERIES"] if c in df.columns]
            df = df[keep].drop_duplicates().reset_index(drop=True)
            df = df.rename(columns={"NAME OF COMPANY": "NAME", "ISIN NUMBER": "ISIN"})
            for c in ["SYMBOL", "NAME", "ISIN", "SERIES"]:
                if c in df.columns:
                    df[c] = df[c].astype(str).str.strip()
            return df.sort_values("SYMBOL").reset_index(drop=True)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Could not fetch NSE symbols. Last error: {last_err}")

def choose_stock(df: pd.DataFrame) -> str:
    """Simple text search → choose by number."""
    print(f"Loaded {len(df)} NSE symbols (EQ).")
    while True:
        q = input("\nType part of SYMBOL or NAME (or 'q' to quit): ").strip()
        if q.lower() in {"q", "quit", "exit"}:
            sys.exit(0)
        if not q:
            continue
        mask = (df["SYMBOL"].str.contains(q, case=False, na=False) |
                df["NAME"].str.contains(q, case=False, na=False))
        hits = df[mask].head(20)
        if hits.empty:
            print("No matches. Try again.")
            continue
        print("\nMatches:")
        for i, r in enumerate(hits.itertuples(index=False), 1):
            print(f"{i:2d}. {r.SYMBOL:<12} [{getattr(r, 'SERIES', '')}]  {r.NAME}")
        sel = input("Pick a number (or 'r' to refine search): ").strip().lower()
        if sel in {"r", "refine"}:
            continue
        if not sel.isdigit():
            print("Enter a number.")
            continue
        idx = int(sel)
        if not (1 <= idx <= len(hits)):
            print("Out of range.")
            continue
        return hits.iloc[idx - 1]["SYMBOL"]

def warm_nse_session(symbol: Optional[str] = None, warm_corp: bool = False) -> requests.Session:
    """Pretend to be a browser + warm cookies so NSE APIs behave."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    })
    try:
        s.get("https://www.nseindia.com/", timeout=10)
    except requests.RequestException:
        pass

    # Warm the quote page (helps LTP)
    if symbol:
        try:
            s.get(f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}", timeout=10)
        except requests.RequestException:
            pass

    # NEW: Warm the *corporate filings shareholding pattern* page (helps promoter JSON)
    if warm_corp and symbol:
        try:
            s.get(
                f"https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern"
                f"?symbol={symbol}&tabIndex=equity",
                timeout=12
            )
        except requests.RequestException:
            pass

    return s

def get_live_price_nse(symbol: str) -> Optional[float]:
    """Fetch live LTP from NSE quote API (simple retries)."""
    s = warm_nse_session(symbol)
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    for _ in range(3):
        try:
            r = s.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            p = (data.get("priceInfo") or {}).get("lastPrice")
            if p is not None:
                return float(p)
        except Exception:
            pass
    return None

def normalize_history_df(df: pd.DataFrame, ysym: str) -> pd.DataFrame:
    """Flatten yfinance columns and keep numeric OHLCV."""
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        try:
            if ysym in df.columns.get_level_values(-1):
                df = df.xs(ysym, axis=1, level=-1)
            else:
                df.columns = df.columns.get_level_values(0)
        except Exception:
            df.columns = df.columns.get_level_values(0)
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors="coerce")
        df = df[~df.index.isna()]
    need = ["Open", "High", "Low", "Close", "Volume"]
    exists = [c for c in need if c in df.columns]
    if not exists:
        return pd.DataFrame()
    df = df[exists].copy()
    for c in exists:
        col = df[c]
        if isinstance(col, pd.DataFrame):
            col = col.iloc[:, 0]
        df[c] = pd.to_numeric(col, errors="coerce")
    df = df.dropna(subset=["Open", "High", "Low", "Close"])
    return df

def fetch_history_yahoo(symbol: str, period="6mo", interval="1d") -> Optional[pd.DataFrame]:
    """6-month daily candles for plotting a simple line chart."""
    ysym = f"{symbol}.NS"
    try:
        raw = yf.download(ysym, period=period, interval=interval, auto_adjust=False, progress=False)
        if raw is None or raw.empty:
            return None
        df = normalize_history_df(raw, ysym)
        return None if df.empty else df
    except Exception:
        return None

def plot_line(df: pd.DataFrame, symbol: str):
    """Simple line chart of Close."""
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Close"])
    plt.title(f"{symbol} – Close (last {len(df)} trading days)")
    plt.xlabel("Date"); plt.ylabel("Price (INR)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()

# ---- promoter holding (single stock only, simple) ----

def fetch_promoter_holding_quarters(symbol: str) -> Optional[pd.DataFrame]:
    """
    Fetch recent shareholding pattern and extract promoter % by quarter (best-effort).
    Returns DataFrame with ['quarter','promoter_pct'] sorted chronologically.
    """
    s = warm_nse_session(symbol, warm_corp=True)
    endpoints = [
        f"https://www.nseindia.com/api/corporate-shareholdings?symbol={symbol}",
        f"https://www.nseindia.com/api/corporates-shareholdings?index=equities&symbol={symbol}",
    ]
    data = None
    for url in endpoints:
        try:
            r = s.get(url, timeout=12)
            if r.status_code != 200:
                continue
            data = r.json()
            break
        except Exception:
            continue
    if data is None:
        return None

    # normalize to list of quarter blocks
    blocks = []
    if isinstance(data, dict):
        for key in ["shareholding", "data", "shareholdingPattern", "shareholdingPtn", "SHP"]:
            val = data.get(key)
            if isinstance(val, list) and val:
                blocks = val; break
    if not blocks and isinstance(data, list):
        blocks = data
    if not blocks:
        return None

    def to_float(x):
        try: return float(str(x).replace("%","").replace(",","").strip())
        except: return None

    def find_promoter_pct(block: dict) -> Optional[float]:
        # search typical places
        lists = ["shareholding","SHP","data","holderData","details","categoryList","shareHolding","shareholdingpattern"]
        hints = ["promoter","promoter group","promoters"]
        candidates = []
        for k in lists:
            arr = block.get(k)
            if isinstance(arr, list):
                for cat in arr:
                    name = (cat.get("category") or cat.get("categoryName") or cat.get("name") or cat.get("holder") or "")
                    lname = str(name).lower()
                    if any(h in lname for h in hints):
                        for f in ["percentage","pctOfTotal","percent","heldPercent","shareholdingPercent",
                                  "sharePct","percentShare","holdingPercent","perc"]:
                            if f in cat and cat[f] is not None:
                                v = to_float(cat[f])
                                if v is not None:
                                    candidates.append(v)
        # fallback: promoter-ish keys at same level
        for k, v in block.items():
            lk = str(k).lower()
            if "promoter" in lk and any(p in lk for p in ["percent","share","holding","pct"]):
                vv = to_float(v)
                if vv is not None:
                    candidates.append(vv)
        candidates = [x for x in candidates if 0 <= x <= 100]
        return max(candidates) if candidates else None

    rows = []
    for blk in blocks:
        q = blk.get("quarter") or blk.get("quarterEnding") or blk.get("quarterEnd") or \
            blk.get("forQuarter") or blk.get("period") or blk.get("date") or \
            blk.get("quarter_ended") or blk.get("qtrEndDate") or blk.get("quarterEndDate")
        pct = find_promoter_pct(blk)
        if q and (pct is not None):
            rows.append({"quarter": str(q), "promoter_pct": pct})

    if not rows:
        return None

    df = pd.DataFrame(rows).dropna().drop_duplicates()

    def quarter_key(q):
        s = str(q)
        m = re.search(r"(\d{4})[-/](\d{1,2})", s)  # 2024-06
        if m: return (int(m.group(1)), int(m.group(2)))
        m = re.search(r"(Q[1-4]).*?(\d{4})", s, re.I)  # Q1 2024
        if m: return (int(m.group(2)), int(m.group(1)[1]))
        return s

    return df.sort_values(by="quarter", key=lambda col: col.map(quarter_key)).reset_index(drop=True)

def show_promoter_trend(symbol: str):
    """Print last few quarters and say if trend is up (net increase over last 3 quarters)."""
    ph = fetch_promoter_holding_quarters(symbol)
    if ph is None or ph.empty:
        print("No promoter data available from NSE for this stock.")
        return
    vals = [round(float(x), 2) for x in ph["promoter_pct"].tolist()]
    qs   = ph["quarter"].tolist()
    last_n = min(6, len(vals))
    print("\nPromoter holding (most recent first):")
    for q, v in zip(qs[-last_n:], vals[-last_n:]):
        print(f"  {q}: {v}%")
    # Simple rule: net increase vs 3 quarters ago
    if len(vals) >= 4 and (vals[-1] - vals[-4]) > 0.0:
        print("➡️  Trend: UP (vs 3 quarters ago)")
    elif len(vals) >= 2 and (vals[-1] - vals[-2]) > 0.0:
        print("➡️  Trend: Slight UP (last quarter)")
    else:
        print("➡️  Trend: Not rising recently")

# ----------
# Main flow (very linear & simple)
# ----------

def main():
    print("Fetching NSE symbols…")
    symbols_df = fetch_symbol_master()

    symbol = choose_stock(symbols_df)
    print(f"\nFetching latest price for: {symbol}")
    ltp = get_live_price_nse(symbol)
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    if ltp is not None:
        print(f"[{now}] {symbol} LTP (NSE live): ₹{ltp:.2f}")
    else:
        print(f"[{now}] Couldn’t get live LTP from NSE (you can still see the chart).")

    # Auto: 6 months, 1-day candles → simple line chart
    hist = fetch_history_yahoo(symbol, period="6mo", interval="1d")
    if hist is None or hist.empty:
        print("No history from Yahoo for the chart.")
    else:
        plot_line(hist, symbol)

    # Optional: promoter holding trend for THIS stock
    do_trend = input("\nCheck promoter holding trend for this stock? (y/N): ").strip().lower()
    if do_trend == "y":
        show_promoter_trend(symbol)

if __name__ == "__main__":
    main()

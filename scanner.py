#!/usr/bin/env python3
# Simple NSE idea scanner (v1)
# - Universe: NIFTY50 (edit UNIVERSE to add more)
# - Metrics: 6m return, distance to 52w high, RSI(14), SMA50/200
# - Output: prints Top 15 + momentum candidates, saves scanner_output.csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import pandas as pd
import yfinance as yf
from tqdm import tqdm

# ---------- Config ----------
NIFTY50 = [
    "RELIANCE","TCS","HDFCBANK","ICICIBANK","INFY","ITC","HINDUNILVR","LT","SBIN","AXISBANK",
    "KOTAKBANK","BHARTIARTL","BAJFINANCE","ADANIENT","ADANIPORTS","HCLTECH","SUNPHARMA","MARUTI",
    "TITAN","ASIANPAINT","ULTRACEMCO","WIPRO","POWERGRID","NTPC","ONGC","TATASTEEL","TATAMOTORS",
    "JSWSTEEL","M&M","TECHM","GRASIM","COALINDIA","HDFCLIFE","DIVISLAB","BRITANNIA","BAJAJFINSV",
    "DRREDDY","CIPLA","EICHERMOT","HEROMOTOCO","BPCL","SHREECEM","NESTLEIND","HINDALCO","INDUSINDBK",
    "SBILIFE","TATACONSUM","APOLLOHOSP"
]
UNIVERSE = NIFTY50         # <- put your own list here later
NEAR_HIGH_PCT = 5.0        # within 5% of 52w high counts as "near"
MIN_BARS = 150        # need enough history for SMA200/RSI
WORKERS = 4

# ---------- Indicators ----------
def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    ma_up = up.rolling(period, min_periods=period).mean()
    ma_down = down.rolling(period, min_periods=period).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def fetch_1y(symbol: str) -> pd.DataFrame | None:
    ysym = f"{symbol}.NS"
    for attempt in range(3):
        try:
            raw = yf.download(
                ysym, period="1y", interval="1d",
                auto_adjust=True, progress=False, threads=False
            )
            # fallback: grab 2y then slice last ~260 trading days
            if raw is None or raw.empty:
                raw = yf.download(
                    ysym, period="2y", interval="1d",
                    auto_adjust=True, progress=False, threads=False
                )
            if raw is None or raw.empty:
                time.sleep(0.6)
                continue

            # Normalize MultiIndex columns if present
            if isinstance(raw.columns, pd.MultiIndex):
                try:
                    if ysym in raw.columns.get_level_values(-1):
                        raw = raw.xs(ysym, axis=1, level=-1)
                    else:
                        raw.columns = raw.columns.get_level_values(0)
                except Exception:
                    raw.columns = raw.columns.get_level_values(0)

            # Keep needed cols and sanitize
            keep = [c for c in ["Open","High","Low","Close","Volume"] if c in raw.columns]
            if not keep:
                time.sleep(0.3); continue

            df = raw[keep].sort_index().copy()
            for c in keep:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            df = df.dropna()

            # If we fetched 2y, trim to last ~260 trading days
            if len(df) > 320:
                df = df.iloc[-260:]

            return df if len(df) >= MIN_BARS else None
        except Exception:
            time.sleep(0.6)
            continue
    return None

def compute_metrics(symbol: str) -> dict | None:
    df = fetch_1y(symbol)
    if df is None or df.empty:
        return None

    close = df["Close"]
    last = float(close.iloc[-1])
    # 6 months ≈ 126 trading days
    start_6m = float(close.iloc[-126])
    ret_6m = (last / start_6m) - 1.0

    high_52w = float(close.max())
    below_high_pct = 100.0 * (high_52w - last) / high_52w if high_52w > 0 else np.nan

    sma50 = float(close.rolling(50).mean().iloc[-1])
    sma200 = float(close.rolling(200).mean().iloc[-1])
    rsi14 = float(rsi(close, 14).iloc[-1])

    momentum_ok = (below_high_pct <= NEAR_HIGH_PCT) and (sma50 > sma200) and (50 <= rsi14 <= 70)

    return {
        "symbol": symbol,
        "last_close": last,
        "ret_6m_pct": ret_6m * 100.0,
        "below_high_pct": below_high_pct,
        "sma50": sma50,
        "sma200": sma200,
        "rsi14": rsi14,
        "momentum_ok": momentum_ok
    }

def scan(symbols: list[str]) -> pd.DataFrame:
    rows = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(compute_metrics, s): s for s in symbols}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Scanning"):
            try:
                r = fut.result()
                if r: rows.append(r)
            except Exception:
                pass
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["ret_6m_pct"]).sort_values("ret_6m_pct", ascending=False).reset_index(drop=True)
    return df

def main():
    symbols = list(dict.fromkeys(UNIVERSE))
    df = scan(symbols)
    if df.empty:
        print("No data fetched. Try again.")
        return
    out = "scanner_output.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved: {out}\n")

    print("Top 15 by 6m return:")
    for i, r in df.head(15).iterrows():
        print(f"{i+1:2d}. {r['symbol']:<12}  6m: {r['ret_6m_pct']:>6.2f}%  "
              f"BelowHigh: {r['below_high_pct']:>5.2f}%  RSI: {r['rsi14']:>5.1f}")

    print("\nMomentum candidates (near 52w high, SMA50>SMA200, RSI 50–70):")
    mm = df[df["momentum_ok"]].sort_values("ret_6m_pct", ascending=False).head(20)
    if mm.empty:
        print("  (none today)")
    else:
        for r in mm.itertuples(index=False):
            print(f" - {r.symbol:<12}  6m: {r.ret_6m_pct:>6.2f}%  "
                  f"BelowHigh: {r.below_high_pct:>5.2f}%  RSI: {r.rsi14:>5.1f}")

if __name__ == "__main__":
    main()

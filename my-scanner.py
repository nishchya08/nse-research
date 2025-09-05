import yfinance as yf
import pandas as pd

# --- pick a stock ---
symbol = "TCS"
ysym = f"{symbol}.NS"


# download 1 year of daily bars
df = yf.download(
    ysym, period="1y",interval="1d",auto_adjust=True,progress=False,threads=False
)

# --- inspect what we got ---
print("Columns:", df.columns.to_list())
print("index type:", type(df.index))
print(df.head(3))
print(df.tail(3))
print("Rows:", len(df))
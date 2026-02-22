import yfinance as yf
import pandas as pd

def scan_top_picks():

    watchlist = ["AAPL","NVDA","MSFT","META","TSLA","AOT.BK","DELTA.BK"]

    results = []

    for ticker in watchlist:
        data = yf.download(ticker, period="3mo", auto_adjust=True)

        if data.empty:
            continue

        # Ensure single-level columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data["MA20"] = data["Close"].rolling(20).mean()

        latest_close = data["Close"].iloc[-1]
        latest_ma20 = data["MA20"].iloc[-1]

        if pd.notna(latest_ma20) and latest_close > latest_ma20:
            results.append({
                "Ticker": ticker,
                "Trend": "Uptrend"
            })

    return pd.DataFrame(results)

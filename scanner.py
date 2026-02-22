import yfinance as yf
import pandas as pd

def scan_top_picks():

    watchlist = ["AAPL","NVDA","MSFT","META","TSLA","AOT.BK","DELTA.BK"]

    results = []

    for ticker in watchlist:
        data = yf.download(ticker, period="3mo")

        if data.empty:
            continue

        data["MA20"] = data["Close"].rolling(20).mean()
        latest = data.iloc[-1]

        if latest["Close"] > latest["MA20"]:
            results.append({
                "Ticker": ticker,
                "Trend": "Uptrend"
            })

    return pd.DataFrame(results)

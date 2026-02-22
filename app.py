import streamlit as st
import yfinance as yf
import pandas as pd
from indicators import calculate_signal
from scanner import scan_top_picks

st.set_page_config(layout="wide")
st.title("📈 Personal Investment Dashboard (FREE Version)")

st.sidebar.header("Your Portfolio")
portfolio_input = st.sidebar.text_area(
    "Enter stocks: TICKER,shares,cost",
    "AAPL,100,170\nNVDA,50,600\nAOT.BK,1000,64"
)

stocks = [line.split(",") for line in portfolio_input.split("\n")]

portfolio_data = []

for ticker, shares, cost in stocks:
    shares = float(shares)
    cost = float(cost)

    data = yf.Ticker(ticker)
    hist = data.history(period="6mo")

    if hist.empty:
        continue

    current_price = hist["Close"].iloc[-1]

    market_value = shares * current_price
    invested_value = shares * cost
    pnl = market_value - invested_value
    pnl_pct = (pnl / invested_value) * 100

    signal = calculate_signal(hist)

    portfolio_data.append({
        "Ticker": ticker,
        "Price": round(current_price,2),
        "P&L %": round(pnl_pct,2),
        "Signal": signal
    })

df = pd.DataFrame(portfolio_data)

st.subheader("📊 Portfolio Overview")
st.dataframe(df)

st.subheader("🔥 Top Picks (Momentum Scanner)")
top_picks = scan_top_picks()
st.dataframe(top_picks)

import streamlit as st
import yfinance as yf
import pandas as pd
import json
from indicators import calculate_signal
from scanner import scan_top_picks

st.set_page_config(layout="wide")

st.title("📊 Yuth's Investment")

# ----------------------------
# Load Saved Portfolio
# ----------------------------

def load_portfolio():
    try:
        with open("portfolio.json", "r") as f:
            return json.load(f)
    except:
        return "AAPL,100,170\nNVDA,50,600\nAOT.BK,1000,64"

def save_portfolio(data):
    with open("portfolio.json", "w") as f:
        json.dump(data, f)

if "portfolio_input" not in st.session_state:
    st.session_state.portfolio_input = load_portfolio()

st.sidebar.header("Your Portfolio")

portfolio_input = st.sidebar.text_area(
    "Enter stocks: TICKER,shares,cost",
    value=st.session_state.portfolio_input,
    height=200
)

if st.sidebar.button("💾 Save Portfolio"):
    save_portfolio(portfolio_input)
    st.sidebar.success("Portfolio Saved to Cloud ✅")

st.session_state.portfolio_input = portfolio_input

# ----------------------------
# FX Rate USD → THB
# ----------------------------

fx = yf.Ticker("THB=X")
fx_rate = fx.history(period="1d")["Close"].iloc[-1]

# ----------------------------
# Portfolio Calculation
# ----------------------------

stocks = [line.split(",") for line in portfolio_input.split("\n") if line]

portfolio_data = []
total_thb = 0

for ticker, shares, cost in stocks:
    shares = float(shares)
    cost = float(cost)

    data = yf.Ticker(ticker)
    hist = data.history(period="6mo")

    if hist.empty:
        continue

    current_price = hist["Close"].iloc[-1]
    market_value = shares * current_price

    # Convert US stocks to THB
    if ".BK" not in ticker:
        market_value_thb = market_value * fx_rate
    else:
        market_value_thb = market_value

    total_thb += market_value_thb

    signal = calculate_signal(hist)

    portfolio_data.append({
        "Ticker": ticker,
        "Value (THB)": round(market_value_thb, 2),
        "Signal": signal
    })

df = pd.DataFrame(portfolio_data)

# ----------------------------
# Display Total Portfolio
# ----------------------------

st.subheader("💰 Total Portfolio Value")
st.metric("Total (THB)", f"{total_thb:,.2f}")

# ----------------------------
# Pie Chart Allocation
# ----------------------------

st.subheader("📊 Allocation (THB)")

if not df.empty:
    pie_data = df.set_index("Ticker")["Value (THB)"]
    st.pyplot(pie_data.plot.pie(autopct="%1.1f%%", figsize=(6,6)).figure)

# ----------------------------
# Portfolio Table
# ----------------------------

st.subheader("📋 Portfolio Breakdown")
st.dataframe(df)

# ----------------------------
# Top Picks
# ----------------------------

st.subheader("🔥 Top Picks (Momentum Scanner)")
top_picks = scan_top_picks()
st.dataframe(top_picks)

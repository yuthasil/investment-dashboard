import streamlit as st
import yfinance as yf
import pandas as pd
import json
import matplotlib.pyplot as plt
from indicators import calculate_signal, calculate_stop_loss
from scanner import scan_top_picks

st.set_page_config(layout="wide")
st.title("📊 Yuth's Investment")

# ----------------------------
# Load / Save Portfolio
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
    st.sidebar.success("Portfolio Saved ✅")

st.session_state.portfolio_input = portfolio_input

# ----------------------------
# FX Rate USD → THB
# ----------------------------

fx = yf.Ticker("THB=X")
fx_rate = round(fx.history(period="1d")["Close"].iloc[-1], 2)

# ----------------------------
# Portfolio Calculation
# ----------------------------

stocks = [line.split(",") for line in portfolio_input.split("\n") if line]

portfolio_data = []
total_thb = 0
total_cost_thb = 0

for ticker, shares, cost in stocks:
    shares = float(shares)
    cost = float(cost)

    data = yf.Ticker(ticker)
    hist = data.history(period="6mo")

    if hist.empty:
        continue

    current_price = hist["Close"].iloc[-1]

    # Moving Averages for Momentum
    hist["MA20"] = hist["Close"].rolling(20).mean()
    hist["MA50"] = hist["Close"].rolling(50).mean()

    ma20 = hist["MA20"].iloc[-1]
    ma50 = hist["MA50"].iloc[-1]

    # Classic momentum logic
    if current_price > ma50 and ma20 > ma50:
        momentum = "BUY"
    elif current_price < ma50 and ma20 < ma50:
        momentum = "SELL"
    else:
        momentum = "HOLD"

    market_value = shares * current_price
    cost_basis = shares * cost

    # Convert US stocks to THB
    if ".BK" not in ticker:
        market_value_thb = market_value * fx_rate
        cost_basis_thb = cost_basis * fx_rate
    else:
        market_value_thb = market_value
        cost_basis_thb = cost_basis

    pnl_thb = market_value_thb - cost_basis_thb
    pnl_pct = (pnl_thb / cost_basis_thb) * 100

    total_thb += market_value_thb
    total_cost_thb += cost_basis_thb

    signal = calculate_signal(hist)
    stop_loss = calculate_stop_loss(hist)

    portfolio_data.append({
        "Ticker": ticker,
        "Current Price": round(current_price, 2),
        "Value (THB)": round(market_value_thb, 2),
        "P&L (THB)": round(pnl_thb, 2),
        "P&L (%)": round(pnl_pct, 2),
        "Momentum": momentum,
        "Signal": signal,
        "Stop Loss": round(stop_loss, 2)
    })

df = pd.DataFrame(portfolio_data)

# ----------------------------
# Portfolio Overview
# ----------------------------

st.subheader("💰 Portfolio Overview")

col1, col2 = st.columns(2)

total_pnl = total_thb - total_cost_thb
total_return_pct = (total_pnl / total_cost_thb) * 100 if total_cost_thb > 0 else 0

col1.metric("Total Value (THB)", f"{total_thb:,.2f}")
col2.metric("Total P&L", f"{total_pnl:,.2f} THB ({total_return_pct:.2f}%)")

# ----------------------------
# Pie Chart (Clean Minimal)
# ----------------------------

st.subheader("📊 Allocation")

if not df.empty:
    pie_data = df.set_index("Ticker")["Value (THB)"]

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        pie_data,
        labels=pie_data.index,
        autopct=None,
        wedgeprops=dict(width=0.4)
    )
    ax.set_title("")
    st.pyplot(fig)

# ----------------------------
# Styled Table
# ----------------------------

st.subheader("📋 Portfolio Breakdown")

def color_columns(val):
    if isinstance(val, (int, float)):
        if val > 0:
            return "color: green"
        elif val < 0:
            return "color: red"
    if val == "BUY":
        return "color: green"
    if val == "SELL":
        return "color: red"
    return ""

styled_df = df.style.applymap(color_columns, subset=["P&L (THB)", "P&L (%)", "Momentum"])
st.dataframe(styled_df, use_container_width=True)

# ----------------------------
# Top Picks
# ----------------------------

st.subheader("🔥 Top Picks (Momentum Scanner)")
top_picks = scan_top_picks()
st.dataframe(top_picks, use_container_width=True)

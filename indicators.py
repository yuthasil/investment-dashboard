import pandas as pd

def calculate_signal(data):

    data["MA50"] = data["Close"].rolling(50).mean()

    exp1 = data["Close"].ewm(span=12).mean()
    exp2 = data["Close"].ewm(span=26).mean()
    data["MACD"] = exp1 - exp2
    data["Signal_Line"] = data["MACD"].ewm(span=9).mean()

    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    latest = data.iloc[-1]

    if latest["MACD"] > latest["Signal_Line"] and latest["RSI"] < 70 and latest["Close"] > latest["MA50"]:
        return "🟢 BUY"
    elif latest["MACD"] < latest["Signal_Line"] and latest["RSI"] > 70:
        return "🔴 SELL"
    else:
        return "🟡 HOLD"

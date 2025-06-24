import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests

st.set_page_config(page_title="Crypto RSI Tracker", layout="wide")

st.title("🧠 Crypto RSI Tracker (Top 20 Daily)")

st.markdown("""
Señales de compra y venta basadas en el RSI diario.
""")

@st.cache_data(ttl=60*5)
def get_top_20_symbols():
    data = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={"vs_currency": "usd","order":"market_cap_desc","per_page":20,"page":1}
    ).json()
    return [c['symbol'].upper()+'USDT' for c in data]

@st.cache_data(ttl=60*5)
def get_rsi(symbol):
    klines = requests.get(
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=50"
    ).json()
    closes = [float(k[4]) for k in klines]
    df = pd.DataFrame(closes, columns=["close"])
    df["rsi"] = ta.rsi(df.close, length=14)
    return round(df.rsi.iloc[-1],2)

top_20 = get_top_20_symbols()

df = pd.DataFrame(columns=["Symbol","RSI","Signal"])

for sym in top_20:
    rsi = get_rsi(sym)
    if rsi <= 20:
        signal = "🟢 BUY"
    elif rsi >= 80:
        signal = "🔴 SELL"
    else:
        signal = "⚪ HOLD"
    df.loc[len(df)] = [sym, rsi, signal]

def color_signal(signal):
    if "BUY" in signal:
        return "background-color: green; color: white"
    elif "SELL" in signal:
        return "background-color: red; color: white"
    return ""

st.dataframe(df.style.applymap(color_signal, subset=["Signal"]), use_container_width=True)
st.caption("Actualizado automáticamente cada 5 minutos.")

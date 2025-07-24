
import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Forex AI Analyzer", layout="wide")
st.title("📈 Forex AI Analyzer with Bollinger Bands")
st.markdown("Analyze real-time Forex market data with Bollinger Bands strategy.")

API_KEY = st.secrets.get("API_KEY", "demo")  # Replace 'demo' with your TwelveData API key
symbol = st.text_input("Enter symbol (e.g., EUR/USD):", value="EUR/USD")
interval = st.selectbox("Select interval:", ["1min", "5min", "15min", "30min", "1h"])

if st.button("Fetch & Analyze Data"):
    base_url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": 100,
        "apikey": API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if "values" not in data:
        st.error("Failed to fetch data or invalid symbol.")
    else:
        df = pd.DataFrame(data["values"])
        df = df.rename(columns={"datetime": "time"})
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time")
        df["close"] = pd.to_numeric(df["close"])

        # Bollinger Bands calculation
        period = 20
        df["sma"] = df["close"].rolling(window=period).mean()
        df["std"] = df["close"].rolling(window=period).std()
        df["upper"] = df["sma"] + (2 * df["std"])
        df["lower"] = df["sma"] - (2 * df["std"])

        st.line_chart(df.set_index("time")[["close", "upper", "lower"]])

        # Signal detection
        last_close = df["close"].iloc[-1]
        last_upper = df["upper"].iloc[-1]
        last_lower = df["lower"].iloc[-1]
        last_candle_red = df["close"].iloc[-1] < df["close"].iloc[-2]

        signal = None
        if last_close >= last_upper and last_candle_red:
            signal = "🔻 SELL SIGNAL (Touch upper BB and red candle)"
        elif last_close <= last_lower and not last_candle_red:
            signal = "🔺 BUY SIGNAL (Touch lower BB and green candle)"

        if signal:
            st.subheader("📢 Trade Signal")
            st.success(signal)
        else:
            st.info("No strong signal found based on current strategy.")

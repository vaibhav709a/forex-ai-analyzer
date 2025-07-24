
import streamlit as st
import requests
import pandas as pd
import datetime
import time

# Set your Twelve Data API key
API_KEY = "137b57f565344e8a8e568ccfc6db4696"

st.title("Bollinger Band Alert App (1m)")
pair = st.text_input("Enter Pair (e.g., EUR/USD)", value="EUR/USD")

def get_data(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=100&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()
        if "values" not in data:
            st.error("Failed to fetch data. Check pair format or API.")
            st.text(response.text)
            return None
        df = pd.DataFrame(data["values"])
        df = df.rename(columns={
            "datetime": "time",
            "open": "open",
            "close": "close",
            "high": "high",
            "low": "low"
        })
        df = df.astype(float, errors="ignore")
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time")
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def bollinger_band_strategy(df):
    df["ma"] = df["close"].rolling(window=20).mean()
    df["std"] = df["close"].rolling(window=20).std()
    df["upper"] = df["ma"] + 2 * df["std"]
    df["lower"] = df["ma"] - 2 * df["std"]

    # Signal: Price touches upper band and red candle
    if len(df) > 1:
        last = df.iloc[-1]
        prev = df.iloc[-2]
        if last["close"] < last["open"] and last["high"] >= last["upper"]:
            return "Signal: 🔻 SELL - Red candle touched upper band"
    return None

if pair:
    df = get_data(pair)
    if df is not None:
        st.line_chart(df.set_index("time")[["close", "upper", "lower"]])
        signal = bollinger_band_strategy(df)
        if signal:
            st.success(signal)
        else:
            st.info("No strong signal found in last candle.")

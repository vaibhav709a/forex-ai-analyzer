
import streamlit as st
import pandas as pd
import requests
import datetime

st.set_page_config(layout="wide")
st.title("📈 Forex AI Analyzer (1m/5m)")

API_KEY = st.secrets["api_key"] if "api_key" in st.secrets else st.text_input("Enter your TwelveData API Key", type="password")

symbol = st.text_input("Enter Symbol (e.g., EUR/USD)", "EUR/USD")
converted_symbol = symbol.replace("/", "")

interval = st.selectbox("Select Timeframe", ["1min", "5min"])
limit = st.slider("Number of candles to fetch", 10, 100, 50)

if API_KEY:
    url = f"https://api.twelvedata.com/time_series?symbol={converted_symbol}&interval={interval}&outputsize={limit}&apikey={API_KEY}&format=JSON&dp=5&indicators=bbands"
    response = requests.get(url)
    data = response.json()

    if "values" in data:
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")

        df.rename(columns={"datetime": "time"}, inplace=True)
        df["upper"] = pd.to_numeric(df["upper_band"], errors="coerce")
        df["lower"] = pd.to_numeric(df["lower_band"], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")

        st.subheader("Bollinger Bands")
        st.line_chart(df.set_index("time")[["close", "upper", "lower"]])
    else:
        st.error("Failed to fetch data. Check symbol and API key.")

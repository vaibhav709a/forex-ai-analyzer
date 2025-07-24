
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Bollinger Band AI Signal", layout="wide")

st.title("📈 Bollinger Band AI Signal")
symbol = st.text_input("Enter Symbol (e.g., EUR/USD, BTC/USD):", value="EUR/USD")
interval = st.selectbox("Interval", ["1min", "5min", "15min", "30min", "1h", "4h"])
api_key = st.text_input("Enter Your TwelveData API Key:", type="password")

if st.button("Analyze"):
    if not symbol or not api_key:
        st.warning("Please enter both symbol and API key.")
    else:
        st.info("Fetching data...")
        try:
            response = requests.get(
                f"https://api.twelvedata.com/bbands?symbol={symbol.replace('/', '')}&interval={interval}&outputsize=50&apikey={api_key}"
            )
            data = response.json()

            if "values" not in data:
                st.error("Error: Could not fetch valid data. Please check API key or symbol.")
            else:
                df = pd.DataFrame(data["values"])
                df = df.rename(columns={"datetime": "time"})
                df["time"] = pd.to_datetime(df["time"])
                df["close"] = pd.to_numeric(df["close"])
                df["upper"] = pd.to_numeric(df["upper_band"])
                df["lower"] = pd.to_numeric(df["lower_band"])

                df = df.sort_values("time")
                st.line_chart(df.set_index("time")[["close", "upper", "lower"]])

                latest = df.iloc[-1]
                signal = "❌ No Signal"
                if latest["close"] > latest["upper"]:
                    signal = "🔻 SELL Signal (Touched Upper Band)"
                elif latest["close"] < latest["lower"]:
                    signal = "🔺 BUY Signal (Touched Lower Band)"

                st.subheader("Latest Signal")
                st.success(f"{signal} — at {latest['time']}")
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")

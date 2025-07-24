import streamlit as st
import requests
import datetime
from indicator_utils import analyze_market

st.set_page_config(page_title="Forex AI Analyzer", layout="centered")

st.title("📊 Forex AI Market Analyzer (1m & 5m)")
st.write("Enter a Forex pair to get candle direction prediction based on indicators + pattern logic.")

pair = st.text_input("Enter Forex Pair (e.g., EUR/USD)").upper().replace(" ", "")
image = st.file_uploader("Optional: Upload candlestick chart image (for visual pattern matching)")

if st.button("🔍 Analyze"):
    if not pair:
        st.error("Please enter a valid Forex pair.")
    else:
        with st.spinner("Analyzing market..."):
            result = analyze_market(pair)
            if result.get("error"):
                st.error(result["error"])
            else:
                st.success(f"Prediction for {pair}")
                st.markdown(f"""
                **🕒 Timeframe:** {result['timeframe']}  
                **📈 Direction:** {result['direction']}  
                **✅ Confidence:** {result['confidence']}%  
                **🔍 Reason:** {result['reason']}  
                **📥 Entry Suggestion:** {result['entry']}
                """)
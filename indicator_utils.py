import requests
from statistics import mean

API_KEY = "137b57f565344e8a8e568ccfc6db4696"
BASE_URL = "https://api.twelvedata.com/time_series"

def fetch_data(pair, interval="1min"):
    symbol = pair.replace("/", "")
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
        "outputsize": 20
    }
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    if "values" in data:
        return list(reversed(data["values"]))
    else:
        return None

def calculate_rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = float(closes[i]) - float(closes[i - 1])
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))
    avg_gain = mean(gains) if gains else 0.0001
    avg_loss = mean(losses) if losses else 0.0001
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def analyze_market(pair):
    result = {}
    for tf in ["1min", "5min"]:
        data = fetch_data(pair, tf)
        if not data:
            return {"error": "Failed to fetch data. Check pair format or API."}
        closes = [c["close"] for c in data]
        rsi = round(calculate_rsi(closes), 2)
        last_candle = data[-1]
        prev_candle = data[-2]

        # Simple candle pattern check: Bullish/Bearish Engulfing
        pattern = ""
        if float(prev_candle["close"]) < float(prev_candle["open"]) and float(last_candle["close"]) > float(last_candle["open"]) and float(last_candle["close"]) > float(prev_candle["open"]):
            pattern = "Bullish Engulfing"
        elif float(prev_candle["close"]) > float(prev_candle["open"]) and float(last_candle["close"]) < float(last_candle["open"]) and float(last_candle["close"]) < float(prev_candle["open"]):
            pattern = "Bearish Engulfing"

        if pattern == "Bullish Engulfing" and rsi < 40:
            return {
                "timeframe": tf,
                "direction": "UP",
                "confidence": 91,
                "reason": f"RSI: {rsi} (oversold) + {pattern}",
                "entry": "Next candle open"
            }
        elif pattern == "Bearish Engulfing" and rsi > 60:
            return {
                "timeframe": tf,
                "direction": "DOWN",
                "confidence": 90,
                "reason": f"RSI: {rsi} (overbought) + {pattern}",
                "entry": "Next candle open"
            }

    return {
        "timeframe": "Unknown",
        "direction": "No Clear Signal",
        "confidence": 50,
        "reason": "No strong pattern found",
        "entry": "Wait for confirmation"
    }
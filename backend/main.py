from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
API_KEY = os.getenv("API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)


@app.get("/api/stocks/{symbol}")
async def get_stock_data(symbol: str):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    return process_alpha_vantage_data(response.json())


def process_alpha_vantage_data(raw_data: dict):
    time_series = raw_data.get("Time Series (Daily)", {})
    processed = []
    for date, values in time_series.items():
        processed.append({
            "date": date,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"])
        })

    processed.sort(key=lambda x: x["date"])
    return {
        "symbol": raw_data.get("Meta Data", {}).get("2. Symbol", ""),
        "data": processed
    }


@app.get("/api/search-tickers")
async def search_tickers(query: str):
    ALPHA_VANTAGE_URL = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={API_KEY}"
    try:
        response = requests.get(ALPHA_VANTAGE_URL)
        data = response.json()
        return [{
            "symbol": item["1. symbol"],
            "name": item["2. name"],
            "type": item["3. type"],
            "region": item["4. region"]
        } for item in data.get("bestMatches", [])]
    except Exception as e:
        return {"error": str(e)}

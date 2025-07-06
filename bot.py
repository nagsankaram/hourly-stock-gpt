import yfinance as yf
import requests
import os
import csv
from datetime import datetime
from xml.etree import ElementTree
import urllib.parse

# === CONFIG ===
CHUNK_SIZE = 50
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://nagsankaram.github.io",
    "X-Title": "StockAdvisorGPT"
}
# ==============

def load_tickers():
    with open("tickers.csv", "r") as f:
        return [row[0].strip() for row in csv.reader(f) if row]

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def get_news_for_ticker(ticker):
    company = ticker.replace(".NS", "")
    url = f"https://finance.yahoo.com/rss/headline?s={urllib.parse.quote(company)}"
    try:
        resp = requests.get(url, timeout=5)
        tree = ElementTree.fromstring(resp.content)
        items = tree.findall('.//item')[:2]  # top 2 headlines
        headlines = [item.find('title').text for item in items]
        return " | ".join(headlines)
    except Exception:
        return "No recent news."

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        price = info.get("previousClose")
        change = info.get("regularMarketChangePercent")
        pe = info.get("trailingPE")
        news = get_news_for_ticker(ticker)
        return f"{ticker}: ₹{price}, {change}%, PE: {pe} | News: {news}"
    except Exception:
        return None

def get_chunks(ticker_list):
    chunks = []
    for chunk in chunk_list(ticker_list, CHUNK_SIZE):
        lines = []
        for ticker in chunk:
            line = get_stock_info(ticker)
            if line:
                lines.append(line)
        chunks.append("\n".join(lines))
    return chunks

def run_llm_conversation(chunks):
    messages = [
        {
            "role": "system",
            "content": "You are a professional Indian stock market analyst. Use fundamentals and news sentiment to recommend stocks."
        }
    ]

    for i, chunk in enumerate(chunks):
        messages.append({
            "role": "user",
            "content": f"Here are {CHUNK_SIZE} stocks:\n{chunk}\nReview and store insights."
        })
        messages.append({
            "role": "assistant",
            "content": "Got it. Reviewed."
        })

    messages.append({
        "role": "user",
        "content": """Now based on all reviewed data:
- Recommend 2 SHORT-TERM trades (1–5 days) based on momentum or news triggers
- Recommend 2 MID-TERM stocks (1–4 weeks) showing trend strength
- Recommend 2 LONG-TERM investments (6+ months) with strong fundamentals and positive sentiment

For each, explain in 1 line. Use ticker symbol and clear reason."""
    })

    data = {
        "model": "mistral/mixtral-8x7b-instruct",
        "messages": messages
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=HEADERS, json=data)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM error: {e}"

def save_report(content):
    now = datetime.now().strftime("%d-%b %I:%M %p")
    with open("report.md", "w") as f:
        f.write(f"📊 **Hourly Stock Picks** – {now}\n\n{content}")

def main():
    tickers = load_tickers()
    chunks = get_chunks(tickers)
    result = run_llm_conversation(chunks)
    save_report(result)
    print(result)

if __name__ == "__main__":
    main()

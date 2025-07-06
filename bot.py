import os
import requests
import csv
from datetime import datetime

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"

def read_ticker_lines():
    lines = []
    with open("tickers.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row["Symbol"]
            cmp = row["CMP"]
            if symbol and cmp and symbol != ".NS":
                lines.append(f"{symbol} — CMP ₹{cmp}")
    return lines

def ask_llm(prompt):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(TOGETHER_URL, headers=headers, json=body)
        result = response.json()
        if "choices" not in result:
            print("LLM error:", result)
            return "❌ LLM returned no valid response.\n\n" + str(result)
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ LLM API call failed:", e)
        return f"❌ LLM API call failed: {e}"

def generate_prompt(ticker_lines):
    return f"""
You are a professional Indian stock trader and advisor.

Below are current CMPs (Current Market Prices) for 500 stocks:

{chr(10).join(ticker_lines)}

Classify 3–5 stocks into each of the following categories:
- 📉 Short-term (1–5 days)
- 📈 Mid-term (2–8 weeks)
- 🏦 Long-term (3+ months)

Use this format exactly:
- SYMBOL — Entry: ₹XXX, Target: ₹YYY, Stop Loss: ₹ZZZ — Reason: ...

✅ Don't repeat any stock in multiple categories.
✅ Ensure entry price is near CMP. Be precise and concise.
"""

def main():
    ticker_lines = read_ticker_lines()
    if not ticker_lines:
        print("⚠️ No valid tickers found in tickers.csv")
        return

    prompt = generate_prompt(ticker_lines[:500])
    response = ask_llm(prompt)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    markdown = f"# 📈 Hourly Stock GPT Report ({timestamp})\n\n{response}"

    with open("report.md", "w") as f:
        f.write(markdown)

    with open("index.md", "w") as f:
        f.write(markdown)

    print("✅ Report written to report.md and index.md")

if __name__ == "__main__":
    main()

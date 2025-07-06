import os
import requests
import csv
from datetime import datetime

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"

def read_tickers():
    with open("tickers.csv", "r") as f:
        return [line.strip() for line in f if line.strip() and line.strip() != ".NS"]

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

def generate_prompt(tickers):
    return f"""
You are a professional Indian stock trader and advisor.

Analyze the following 500 NSE stock tickers and recommend investments in 3 categories:
- Short-term (1–5 days)
- Mid-term (2–8 weeks)
- Long-term (3+ months)

📌 For each category, list 3–5 stocks using this format:

- TICKER — Entry: ₹XXX, Target: ₹YYY, Stop Loss: ₹ZZZ — Reason: ...

✅ Do NOT repeat any company in multiple categories.
✅ Only use tickers from this list: {', '.join(tickers)}
✅ Be concise and specific.
"""

def main():
    tickers = read_tickers()
    if not tickers:
        print("⚠️ No valid tickers found in tickers.csv")
        return

    prompt = generate_prompt(tickers[:500])
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

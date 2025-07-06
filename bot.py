import os
import requests
import csv
import shutil
from datetime import datetime

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat-v3-0324:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def read_tickers():
    with open("tickers.csv", "r") as f:
        return [line.strip() for line in f if line.strip() and line.strip() != ".NS"]

def ask_llm(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=body)
    result = response.json()

    if "choices" not in result:
        print("LLM error:", result)
        return "❌ LLM returned no valid response."

    return result["choices"][0]["message"]["content"]

def generate_prompt(tickers):
    return f"""
You are an expert Indian stock advisor. Analyze the following 500 stocks and give today's investment recommendations.

Tickers: {', '.join(tickers)}

Classify them into:
- Short-term (1–5 days)
- Mid-term (2–8 weeks)
- Long-term (3+ months)

For each category, recommend 3–5 stocks with a one-line reason. Avoid repeating company names across categories.
"""

def main():
    tickers = read_tickers()
    if not tickers:
        print("⚠️ No valid tickers to process.")
        return

    prompt = generate_prompt(tickers[:500])  # limit prompt size
    response = ask_llm(prompt)

    with open("report.md", "w") as f:
        f.write(f"# Hourly Stock GPT Report ({datetime.now().isoformat()})\n\n")
        f.write(response)

    # ✅ Show on GitHub Pages
    shutil.copy("report.md", "index.md")
    print("✅ Report generated and published as index.md")

if __name__ == "__main__":
    main()

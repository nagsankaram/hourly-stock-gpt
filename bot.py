import os
import requests
import csv
from datetime import datetime

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mixtral-8x7b"  # or another supported free model
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def read_tickers():
    with open("tickers.csv", "r") as f:
        return [line.strip() for line in f.readlines()]

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

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
You are a professional Indian stock advisor. Analyze the following 50 tickers for today's short-term, mid-term, and long-term investment opportunities.

Tickers: {', '.join(tickers)}

Give separate lists for short-term (1–5 days), mid-term (2–8 weeks), and long-term (3+ months). Mention 3–5 tickers per category with a reason for each. Be concise.
"""

def main():
    tickers = read_tickers()
    all_outputs = []

    for chunk in chunk_list(tickers, 50):
        prompt = generate_prompt(chunk)
        response = ask_llm(prompt)
        all_outputs.append(response)

    final_output = "\n\n".join(all_outputs)

    with open("report.md", "w") as f:
        f.write(f"# Hourly Stock GPT Report ({datetime.now().isoformat()})\n\n")
        f.write(final_output)

    print("✅ Report generated as report.md")

if __name__ == "__main__":
    main()

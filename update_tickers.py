import requests
import csv

def update_tickers():
    url = "https://www1.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print("Failed to fetch tickers")
        return

    lines = r.text.strip().splitlines()
    reader = csv.DictReader(lines)
    tickers = []

    for row in reader:
        symbol = row["Symbol"].strip()
        if not symbol.endswith(".NS"):
            symbol += ".NS"
        tickers.append(symbol)

    with open("tickers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for t in tickers:
            writer.writerow([t])

    print(f"Updated {len(tickers)} tickers.")

if __name__ == "__main__":
    update_tickers()

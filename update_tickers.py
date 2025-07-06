import requests
import csv

def update_tickers():
    # NSE blocks requests without proper headers
    url = "https://www1.nseindia.com/content/indices/ind_nifty500list.csv"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www1.nseindia.com/"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200 or "html" in response.text.lower():
        raise Exception("Failed to fetch CSV. NSE may be blocking the request.")

    lines = response.text.strip().splitlines()
    reader = csv.reader(lines)
    next(reader)  # skip header

    tickers = []
    for row in reader:
        if len(row) < 2:
            continue
        symbol = row[2].strip() if len(row) >= 3 else row[0].strip()
        if not symbol.endswith(".NS"):
            symbol += ".NS"
        tickers.append(symbol)

    with open("tickers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for t in tickers:
            writer.writerow([t])

    print(f"✅ Updated {len(tickers)} tickers.")

if __name__ == "__main__":
    update_tickers()

import requests
from bs4 import BeautifulSoup
import csv

def update_tickers():
    url = "https://www.screener.in/screens/339816/top-500/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception("Failed to fetch Screener.in data")

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="data-table")
    if not table:
        raise Exception("Could not find stock table in Screener HTML")

    rows = table.find_all("tr")[1:]  # Skip header row

    tickers = []
    for row in rows:
        link = row.find("a", href=True)
        if link:
            # Extract company slug from URL: /company/TATAMOTORS/consolidated/
            parts = link["href"].split("/")
            if len(parts) > 2:
                symbol = parts[2].strip().upper()
                if symbol and not symbol.endswith(".NS"):
                    symbol += ".NS"
                tickers.append(symbol)

    with open("tickers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for t in tickers:
            writer.writerow([t])

    print(f"✅ Updated {len(tickers)} tickers from Screener.in")

if __name__ == "__main__":
    update_tickers()

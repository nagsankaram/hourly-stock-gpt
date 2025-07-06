import requests
from bs4 import BeautifulSoup
import csv

def update_tickers():
    url = "https://www.screener.in/screens/2918344/top-500-quality/"
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

    rows = table.find_all("tr")[1:]  # Skip table header
    stocks = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        link = cols[0].find("a", href=True)
        if not link:
            continue

        try:
            symbol = link["href"].split("/")[2].strip().upper()
            if not symbol.endswith(".NS"):
                symbol += ".NS"

            # Optional data fields
            market_cap = parse_float(cols[1].text)
            current_price = parse_float(cols[2].text)
            change_percent = parse_float(cols[3].text)
            volume = parse_int(cols[4].text)
            pe_ratio = parse_float(cols[5].text)

            # Custom scoring formula (tune as needed)
            score = (volume * abs(change_percent)) / (pe_ratio + 1)

            stocks.append({
                "symbol": symbol,
                "score": score
            })
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue

    # Sort by score descending
    sorted_stocks = sorted(stocks, key=lambda x: x["score"], reverse=True)

    # Take top 500
    top_500 = sorted_stocks[:500]

    with open("tickers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for stock in top_500:
            writer.writerow([stock["symbol"]])

    print(f"✅ Saved top {len(top_500)} tickers to tickers.csv")

# Utility functions
def parse_float(text):
    try:
        return float(text.replace(",", "").replace("%", "").strip())
    except:
        return 0.0

def parse_int(text):
    try:
        return int(text.replace(",", "").strip())
    except:
        return 0

if __name__ == "__main__":
    update_tickers()

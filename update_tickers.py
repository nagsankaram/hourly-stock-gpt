import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://www.screener.in/screens/2918344/top-500-quality/?page="

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

def update_tickers():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    stocks = []
    page = 1

    while True:
        print(f"🔄 Fetching page {page}...")
        r = requests.get(BASE_URL + str(page), headers=headers)
        if r.status_code != 200:
            print(f"❌ Failed to load page {page}")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="data-table")
        if not table:
            print(f"✅ No table found on page {page}, ending loop.")
            break

        rows = table.find_all("tr")[1:]  # skip the header
        stock_rows = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue
            if cols[0].find("a", href=True):
                stock_rows.append(row)

        print(f"🔍 Found {len(stock_rows)} stock rows on page {page}")
        if len(stock_rows) == 0:
            break

        for row in stock_rows:
            cols = row.find_all("td")
            try:
                symbol = cols[0].find("a")["href"].split("/")[2].strip().upper()
                if not symbol.endswith(".NS"):
                    symbol += ".NS"

                market_cap = parse_float(cols[1].text)
                current_price = parse_float(cols[2].text)
                change_percent = parse_float(cols[3].text)
                volume = parse_int(cols[4].text)
                pe_ratio = parse_float(cols[5].text)

                score = (volume * abs(change_percent)) / (pe_ratio + 1)

                stocks.append({
                    "symbol": symbol,
                    "score": score
                })

            except Exception as e:
                print(f"⚠️ Skipped row due to error: {e}")
                continue

        page += 1

    print(f"📊 Total stocks collected: {len(stocks)}")
    sorted_stocks = sorted(stocks, key=lambda x: x["score"], reverse=True)
    top_500 = sorted_stocks[:500]

    with open("tickers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for stock in top_500:
            writer.writerow([stock["symbol"]])

    print(f"✅ Saved top {len(top_500)} tickers to tickers.csv")

if __name__ == "__main__":
    update_tickers()

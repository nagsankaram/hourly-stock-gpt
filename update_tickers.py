import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://www.screener.in/screens/2918344/top-500-quality/?page="
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

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
    stocks = []
    page = 1

    while True:
        print(f"🔄 Fetching page {page}...")
        url = f"{BASE_URL}{page}"
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"❌ Failed to load page {page}")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", class_="data-table")
        if not table:
            print(f"❌ No table found on page {page}")
            break

        rows = table.select("tr[data-row-company-id]")
        print(f"✅ Found {len(rows)} stock rows")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue
            link = cols[1].find("a", href=True)
            if not link:
                continue

            try:
                href = link["href"]
                parts = href.strip("/").split("/")
                if len(parts) >= 2 and parts[0] == "company":
                    symbol = parts[1].upper()
                    if not symbol.endswith(".NS"):
                        symbol += ".NS"
                else:
                    continue

                price = parse_float(cols[2].text)
                pe = parse_float(cols[3].text)
                roce = parse_float(cols[10].text) if len(cols) > 10 else 0
                volume = parse_int(cols[11].text) if len(cols) > 11 else 0

                if not symbol or symbol == ".NS":
                    continue

                score = (volume * roce) / (pe + 1)

                stocks.append({
                    "symbol": symbol,
                    "cmp": price,
                    "score": score,
                    "roce": roce,
                    "volume": volume
                })

            except Exception as e:
                print(f"⚠️ Error parsing row: {e}")
                continue

        if len(rows) < 25:
            break
        page += 1
        if page > 26:
            break

    print(f"📊 Total stocks scraped: {len(stocks)}")
    top = sorted(stocks, key=lambda x: x["score"], reverse=True)[:200]

    with open("tickers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Symbol", "CMP", "Score", "ROCE", "Volume"])
        for stock in top:
            writer.writerow([
                stock["symbol"],
                stock["cmp"],
                stock["score"],
                stock["roce"],
                stock["volume"]
            ])

    print(f"✅ Saved {len(top)} tickers to tickers.csv")

if __name__ == "__main__":
    update_tickers()

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

    # Dump response HTML for debugging if needed
    with open("debug_screener.html", "w", encoding="utf-8") as debug_file:
        debug_file.write(r.text)

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="data-table")
    if not table:
        raise Exception("Could not find stock table in Screener HTML")

    rows = table.find_all("tr")[1:]
    print(f"🔍 Found {len(rows)} stock rows")

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

            market_cap = parse_float(cols[1].text)
            current_price = parse_float(cols[2].text)
            change_percent = parse_float(cols[3].text)
            volume = parse_int(cols[4].text)
            pe_ratio = parse_float(cols[5].text)

            score = (volume * abs(change_percent)) / (pe_ratio + 1)

            print(f"Parsed: {symbol} | Vol: {volume}, Δ%: {change_percent}, PE: {pe_ratio}, Score: {score:.2f}")

            stocks.append({
                "symbol": symbol,
                "score": score
            })

        except Exception as e:
            print(f"⚠️ Skipped row due to error: {e}")
            continue

    sorted_stocks = sorted(stocks, key=lambda x: x["score"], reverse=True)
    top_500 = sorted_stocks[:500]

    with open("tickers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for stock in top_500:
            writer.writerow([stock["symbol"]])

    print(f"✅ Saved top {len(top_500)} tickers to tickers.csv")

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

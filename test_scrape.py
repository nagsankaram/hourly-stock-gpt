# test_scrape.py
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def scrape(page=1):
    url = f"https://www.screener.in/screens/2918344/top-500-quality/?page={page}"
    print(f"Fetching page {page}...")
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="data-table")
    rows = table.find_all("tr")[1:]
    print(f"Found {len(rows)} rows.")
    for row in rows[:5]:
        cols = row.find_all("td")
        print(cols[0].text.strip())

scrape(1)
scrape(2)
scrape(3)

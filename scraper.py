import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

dynamic_pages = [
    "https://www.gmuniversity.ac.in/notice.php",
]
os.makedirs("data/text", exist_ok=True)
os.makedirs("data/pdfs", exist_ok=True)


def download_pdfs_from_table(url):
    print("Checking PDFs in:", url)
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            print("No table found:", url)
            return

        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            # columns: Sl No | Date | Title | Download
            date_text  = cols[1].get_text(strip=True)   # e.g. "26/03/2026"
            title_text = cols[2].get_text(strip=True)   # e.g. "FORM FILL UP NOTICE"

            link = row.find("a")
            if not link:
                continue

            href = link.get("href")
            if not href or ".pdf" not in href.lower():
                continue

            if not href.startswith("http"):
                href = urljoin(url, href)

            pdf_name = href.split("/")[-1]
            pdf_path = f"data/pdfs/{pdf_name}"

            # always write/update metadata json (date+title stay fresh on every scrape)
            meta = {"url": href, "date": date_text, "title": title_text}
            with open(f"data/pdfs/{pdf_name}.meta.json", "w", encoding="utf-8") as f:
                json.dump(meta, f)

            if os.path.exists(pdf_path):
                print(f"Already downloaded: {pdf_name}")
                continue

            pdf_data = requests.get(href)
            with open(pdf_path, "wb") as f:
                f.write(pdf_data.content)
            print(f"Downloaded: {pdf_name}  [{date_text}]  {title_text}")

    except Exception as e:
        print("PDF scan failed:", url, "→", e)


print("\nStarting Web Scraper\n")

for page in dynamic_pages:
    download_pdfs_from_table(page)

print("\nScraping Completed\n")
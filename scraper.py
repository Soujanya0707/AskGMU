import requests
from bs4 import BeautifulSoup
import os
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
        notices = []
        
        for link in table.find_all("a"):
            href = link.get("href")
            if href and ".pdf" in href.lower():
                if not href.startswith("http"):
                    href = urljoin(url, href)
                pdf_name = href.split("/")[-1]
                path = f"data/pdfs/{pdf_name}"

                url_path = f"data/pdfs/{pdf_name}.url"
                with open(url_path, "w") as f:
                    f.write(href)

                if os.path.exists(path):
                    continue
                pdf_data = requests.get(href)
                with open(path, "wb") as f:
                    f.write(pdf_data.content)
                print("Downloaded:", pdf_name)
    except Exception as e:
        print("PDF scan failed:", url, "→", e)


print("\nStarting Web Scraper\n")

for page in dynamic_pages:
    download_pdfs_from_table(page)

print("\nScraping Completed\n")
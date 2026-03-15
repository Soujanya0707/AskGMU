import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

core_pages = [ "https://www.gmuniversity.ac.in/departments/computer-science/",
              "https://www.gmuniversity.ac.in/oic-admission.php"
   # "https://www.gmuniversity.ac.in/",
  #  "https://www.gmuniversity.ac.in/about-us/",
   # "https://www.gmuniversity.ac.in/admissions/",
   # "https://www.gmuniversity.ac.in/academics/"
]

dynamic_pages = [
   # "https://www.gmuniversity.ac.in/notice/",
]

# directories for saving
os.makedirs("data/text", exist_ok=True)
os.makedirs("data/pdfs", exist_ok=True)


def scrape_text(url):
    print("Scraping:", url)
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")
        text = ""

        for p in paragraphs:
            text += p.get_text() + "\n"

        filename = url.replace("https://", "").replace("/", "_")

        with open(f"data/text/{filename}.txt", "w", encoding="utf-8") as f:
            f.write(text)

    except Exception as e:
        print("Failed to scrape:", url, "→", e)


def download_pdfs(url):
    print("Checking PDFs in:", url)
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all("a")

        for link in links:
            href = link.get("href")

            if href and ".pdf" in href.lower():
                if not href.startswith("http"):
                    href = urljoin(url, href)

                pdf_name = href.split("/")[-1]
                path = f"data/pdfs/{pdf_name}"

                if os.path.exists(path):
                    continue

                pdf_data = requests.get(href)

                with open(path, "wb") as f:
                    f.write(pdf_data.content)

                print("Downloaded:", pdf_name)

    except Exception as e:
     print("PDF scan failed:", url, "→", e)


print("\nStarting Web Scraper\n")

# Scrape core pages
for page in core_pages:
    scrape_text(page)
    download_pdfs(page)

# Scrape dynamic pages + PDFs
for page in dynamic_pages:
    scrape_text(page)
    download_pdfs(page)

print("\nScraping Completed\n")

# print(soup.prettify()[:2000])



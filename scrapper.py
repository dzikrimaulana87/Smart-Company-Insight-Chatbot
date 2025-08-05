import requests
from bs4 import BeautifulSoup
import os
import re

def fetch_clean_text(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Gagal ambil {url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Hapus tag yang tidak relevan
    for tag in soup(["script", "style", "noscript", "footer", "header", "nav"]):
        tag.decompose()

    text = soup.get_text(separator=' ')
    cleaned_text = re.sub(r'\s+', ' ', text).strip()

    return cleaned_text


def save_text_to_file(text, filename, folder="data"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def scrape_company_pages(company_data):
    company_name = company_data.get("Company", "Unknown Company")
    urls = [(company_data.get("Website", "")),(f"{company_data.get('Website', '')}/about"), (f"{company_data.get('Website', '')}/about-us")]

    summary = f"{company_name} is a {company_data.get('Industry', 'N/A')} located in {company_data.get('City', 'N/A')}, {company_data.get('State', 'N/A')}."

    combined_text = f"== Company Summary ==\n{summary}\n\n"

    for url in urls:
        if not url or url == "NA":
            continue
        print(f"[INFO] Scraping: {url}")
        content = fetch_clean_text(url)
        combined_text += f"{content}"

    filename = "scraped_content.txt"
    save_text_to_file(combined_text, filename)
    print(f"[DONE] Saved enriched content for {company_name} to {filename}")

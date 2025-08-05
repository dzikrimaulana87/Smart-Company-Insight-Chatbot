import requests
from bs4 import BeautifulSoup
import os
import re
from io import StringIO


def fetch_clean_text(url):
    
    '''
    This function fetches the content of a given URL'''
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Delete unnecessary tags
    for tag in soup(["script", "style", "noscript", "footer", "header", "nav"]):
        tag.decompose()

    # Take all tetx
    text = soup.get_text(separator=' ')

    # clean all space and newlines
    cleaned_text = re.sub(r'\s+', ' ', text).strip()

    return cleaned_text

def save_text_to_file(text, filename, folder="data"):
    '''
    This function saves the given text to a file in the specified folder.
    '''
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def scrape_company_pages(company_name, urls):
    ''' This function scrapes the content from a list of URLs related to a company'''
    combined_text = ""
    for url in urls:
        print(f"[INFO] Scraping: {url}")
        text = fetch_clean_text(url)
        combined_text += f"\n\n== Content from {url} ==\n{text}"
    
    filename = f"{company_name.lower().replace(' ', '_')}.txt"
    save_text_to_file(combined_text, filename)
    print(f"[DONE] Saved content for {company_name} to {filename}")

# --- Sample usage ---
if __name__ == "__main__":
    company_name = "Wayside Inn Grist Mill"
    urls = [
        "http://www.wayside.org/planning-your-visit/grist-mill",  # landing page
        "http://www.wayside.org/about-us"  # jika ada halaman about
    ]
    scrape_company_pages(company_name, urls)

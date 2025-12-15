import os, re, json, time, tldextract, logging
from urllib.parse import urljoin, urldefrag
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment
load_dotenv()
SEED_URL = os.getenv("SEED_URL", "")
MAX_PAGES = int(os.getenv("MAX_PAGES", "40"))
RAW_DIR = "data/raw"
CLEAN_DIR = "data/clean"

# Setup directories
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

def same_domain(base, link):
    b = tldextract.extract(base)
    l = tldextract.extract(link)
    return (b.domain, b.suffix) == (l.domain, l.suffix)

def normalize_url(base, href):
    if not href:
        return None
    href = urljoin(base, href)
    href, _ = urldefrag(href)
    if href.startswith(("mailto:", "tel:")):
        return None
    return href

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript", "header", "footer", "nav", "form"]):
        t.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def crawl():
    visited, queue = set(), [SEED_URL]
    pages = 0
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/117.0 Safari/537.36"
    }

    with httpx.Client(headers=headers, follow_redirects=True, timeout=20.0) as client:
        logging.info(f"Starting crawl from {SEED_URL} (max {MAX_PAGES} pages)")
        while queue and pages < MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue
            try:
                r = client.get(url)
                r.raise_for_status()
                html = r.text
            except Exception as e:
                logging.warning(f"Failed: {url} ({e.__class__.__name__})")
                continue

            visited.add(url)
            pages += 1
            logging.info(f"[{pages}/{MAX_PAGES}] Crawled: {url}")

            raw_path = os.path.join(RAW_DIR, f"{pages:05d}.json")
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump({"url": url, "html": html}, f, ensure_ascii=False)

            text = clean_text(html)
            if not text.strip():
                logging.warning(f"Skipped empty page: {url}")
                continue

            clean_path = os.path.join(CLEAN_DIR, f"{pages:05d}.txt")
            with open(clean_path, "w", encoding="utf-8") as f:
                f.write(f"URL: {url}\n\n{text}\n")

            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                link = normalize_url(url, a["href"])
                if link and same_domain(SEED_URL, link) and link not in visited and link not in queue:
                    queue.append(link)
            time.sleep(0.1)

        logging.info(f"Crawl finished. Pages saved: {pages}")
        logging.info(f"Clean text files in: {os.path.abspath(CLEAN_DIR)}")

if __name__ == "__main__":
    crawl()

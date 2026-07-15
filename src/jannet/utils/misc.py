import re
import requests
from src.jannet.utils.parsing import reformat_html_tags, html_to_clean
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))


def extract_words(text):
    stemmer = PorterStemmer()
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    filtered_words = [
        stemmer.stem(word)
        for word in words
        if word not in stop_words

    ] + words

    return filtered_words


def make_getr(url):
    url = url.strip()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    if not url.startswith("http"):
        url = "https://" + url
    url = url.rstrip("/")

    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        return response

    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        raise

def make_postr(url, json):
    url = url.strip()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*", # Updated to match your JSON data context
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.post(url, json=json, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        return response

    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        raise




def site_details(url=None, content=None):  #extract details from the given content, if given
    if content is None and url is not None:
        try:
            response = make_getr(url)
            content = response.text

        except requests.RequestException as e:
            print(f"Request failed for {url}")
            return "No title available", "No description available", "No content available"

    if content:
        page_contents = reformat_html_tags(content)
        reformatted_content = html_to_clean(content)
        description = page_contents.description[0] if len(page_contents.description) > 0 else "No description available"
        title = page_contents.title[0] if len(page_contents.title) > 0 else "No title available"

        return title, description, reformatted_content
    else:
        return "No title available", "No description available", "No content available"



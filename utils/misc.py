import re
import requests
from utils.parsing import reformat_html_tags, html_to_clean
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import numpy as np

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


def make_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    if not url.startswith("http"):
        url = "https://" + url
    url = url.rstrip("/")

    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        return response

    except requests.RequestException as e:
        print(f"Request failed for {url}")
        return e


def site_details(url=None, content=None):  #extract details from the given content, if given
    if content is None and url is not None:
        try:
            response = make_request(url)
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



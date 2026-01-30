import re
import requests

from utils.regex import reformat_html_tags

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import numpy as np

stop_words = set(stopwords.words('english'))


def clamp_search_term(term):
    if len(term.split()) > 1:
        #stick words side by side
        terms = term.split()
        alt_list = []
        for term in terms:
            term = term.strip()
            alt_list.append(term + term[::-1])

        return alt_list
    else:
        return []


def extract_keywords(text):
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
        return None


def site_details(url=None, content=None):  #extract details from the given content, if given
    if content is None and url is not None:
        try:
            response = make_request(url)
            content = response.text

        except requests.RequestException as e:
            print(f"Request failed for {url}")
            return "No title available", "No description available", "No content available"

    if content:
        reformatted_content, texts = reformat_html_tags(content)
        description = texts[8][0] if texts[8] else texts[7][0] if texts[7] else texts[6][0] if texts[
            6] else "No description available"
        title = texts[0][0] if texts[0] else "No title available"

        return title, description, reformatted_content
    else:
        return "No title available", "No description available", "No content available"


#below this line is the db misc tools

def cosine_similarity(vector1, vector2):
    vector1 = vector1.flatten()
    vector2 = vector2.flatten()
    similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

    return similarity

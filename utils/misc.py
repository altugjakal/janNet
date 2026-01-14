import re
import requests
import torch
from core.model_manager import get_model
from utils.regex import reformat_html_tags

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from core.model_manager import get_model
import numpy as np
import urllib.parse
from utils.regex import get_tld, get_domain
from math import log1p


stop_words = set(stopwords.words('english'))





def extract_keywords(text):
    global stop_words
    stemmer = PorterStemmer()
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    filtered_words = [
        stemmer.stem(word) 
        for word in words 
        if word not in stop_words

    ]
    
    return filtered_words


def site_details(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })
    except requests.RequestException as e:
        print(f"Request failed for {url}")
        return "No title available", "No description available", "No content available"

    if response.status_code == 200:
        reformatted_content, texts = reformat_html_tags(response.text)
        description = texts[8][0] if texts[8] else texts[7][0] if texts[7] else texts[6][0] if texts[6] else "No description available"
        title = texts[0][0] if texts[0] else "No title available"

        return title, description, reformatted_content
    else:
        return "No title available", "No description available", "No content available"


#below this line is the vectordb misc tools

def cosine_similarity(vector1, vector2):
    vector1 = vector1.flatten()
    vector2 = vector2.flatten()
    similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


    return similarity

def vectorise_text(text):
    model = get_model()

    return model.encode(text)

def encode_tokens(self, text):
    model = get_model()
    inputs = model.tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = self.model[0].auto_model(**inputs)
    return outputs.last_hidden_state.squeeze(0)

def make_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    if not url.startswith("http"):
        url = "https://" + url
    url = url.rstrip("/")

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        return response

    except requests.RequestException as e:
        print(f"Request failed for {url}")
        return

    if response.status_code != 200:
        print(f"Could not find url: {url}")
        return

def rank(url, score):
    url_obj = urllib.parse.urlparse(url)
    importance = score



    domain = get_domain(url)
    tld = get_tld(domain)
    if tld in ['edu']:
        tld_multiplier = 2.0  
    elif tld in ['ac', 'edu.au', 'edu.cn'] or domain.endswith('.ac.uk'):
        tld_multiplier = 2.0  
    elif tld in ['com', 'org', 'net']:
        tld_multiplier = 1.0 
    else:
        tld_multiplier = 0.7

    base_score = log1p(importance) * tld_multiplier
    return base_score

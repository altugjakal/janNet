import re
import requests
from utils.regex import reformat_html_tags

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords


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

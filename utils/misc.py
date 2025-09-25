
import re


def extract_keywords(text):

    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 
        'may', 'might', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 
        'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 
        'your', 'his', 'its', 'our', 'their', 'can', 'also', 'more', 'very',
        'so', 'just', 'like', 'get', 'go', 'come', 'see', 'know', 'take',
        'make', 'way', 'time', 'well', 'good', 'new', 'first', 'last', 'long',
        'great', 'little', 'own', 'other', 'old', 'right', 'big', 'high',
        'different', 'small', 'large', 'next', 'early', 'young', 'important',
        'few', 'public', 'bad', 'same', 'able'
    }
    
    
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    filtered_words = [word for word in words 
        if word not in stop_words and len(word) >= 3]
    

    return filtered_words
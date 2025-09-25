import csv
import json

def write_to_csv(file_path, data, mode='a'):
    
    with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)
        
def read_from_csv(file_path):
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)

def separate_indexes(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'a', 'an', 'this', 'that', 'these', 'those'}
    words = [word for word in words if word not in stop_words and len(word) > 2]
        
    return words

def manage_for_index(url, keywords, importance):

    with open('./csv/indexes.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

   
    

    for keyword in keywords:
        found = False
        for row in rows:
            if row[0] == keyword:
                found = True
                urls_data = json.loads(row[1])
                urls_data[url] = importance
                row[1] = json.dumps(urls_data)
                break
            
        if not found:
            new_row = [keyword, json.dumps({url: importance})]
            rows.append(new_row)

    with open('./csv/indexes.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
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


def remove_from_csv(file_path, data):
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    rows = [row for row in rows if row != data]

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def manage_for_index(url, keywords, importances): #duplicates should add up importance

    with open('./csv/indexes.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    for keyword, importance in zip(keywords, importances):
        found = False
        for row in rows:
            if row and len(row) > 0 and row[0] == keyword:  # Check if row is not empty!
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

def is_url_visited(url):
    urls = read_from_csv("./csv/urls.csv")
    return any(row[0] == url for row in urls)
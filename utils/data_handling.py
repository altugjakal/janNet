import sqlite3
from contextlib import contextmanager
from datetime import datetime
import numpy as np
from utils.misc import cosine_similarity




@contextmanager
def open_db(db_path='db/jannet1.db'):

    conn = sqlite3.connect(db_path)
    try:

        yield conn
    finally:
        conn.close()


def initialize_database(db_path='db/jannet1.db'):

    with open_db(db_path) as conn:
        c = conn.cursor()






        c.execute('''CREATE TABLE IF NOT EXISTS urls
                     (url TEXT PRIMARY KEY,
                      crawled_at TIMESTAMP NOT NULL default CURRENT_TIMESTAMP)''')

        # Queue table
        c.execute('''CREATE TABLE IF NOT EXISTS queue
                     (url TEXT PRIMARY KEY,
                      added_at TIMESTAMP NOT NULL default CURRENT_TIMESTAMP)''')

        # Domains table
        c.execute('''CREATE TABLE IF NOT EXISTS domains
                     (domain TEXT PRIMARY KEY,
                      added_at TIMESTAMP NOT NULL default CURRENT_TIMESTAMP)''')

        # Keyword index table
        c.execute('''CREATE TABLE IF NOT EXISTS keyword_index
                     (keyword TEXT,
                      url TEXT,
                      importance REAL,
                      PRIMARY KEY (keyword, url))''')

        c.execute('''CREATE TABLE IF NOT EXISTS vector_index (
            embedding_id INTEGER NOT NULL,
            url TEXT,
            created_at TEXT NOT NULL default CURRENT_TIMESTAMP,
            PRIMARY KEY (embedding_id, url))'''
            )

        # Create indexes for fast lookups
        c.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON keyword_index(keyword)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_url ON keyword_index(url)')

        conn.commit()


def add_url(url, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO urls (url, crawled_at) VALUES (?, ?)''', (url, datetime.now()))
        conn.commit()


def is_url_visited(url, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM urls WHERE url = ?''', (url,))
        return c.fetchone() is not None


def get_all_urls(db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM urls''')
        return c.fetchall()


def add_to_queue(url, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO queue (url, added_at) VALUES (?, ?)''', (url, datetime.now()))
        conn.commit()


def drop_from_queue(url, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''DELETE FROM queue WHERE url = ?''', (url,))
        conn.commit()


def is_in_queue(url, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM queue WHERE url = ?''', (url,))
        return len(c.fetchall()) > 0


def get_queue(db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM queue''')
        return c.fetchall()


def add_domain(domain, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO domains (domain, added_at) VALUES (?, ?)''', (domain, datetime.now()))
        conn.commit()


def check_domain(domain, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT domain FROM domains WHERE domain = ?''', (domain,))
        return c.fetchone() is not None


def get_domains(db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT domain FROM domains''')
        return c.fetchall()

def manage_vector_for_index(url, emb_id, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO vector_index (embedding_id,
                url) VALUES (?, ?)''', (emb_id, url))
        conn.commit()

def get_url_by_vector_id(vector_id, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM vector_index WHERE embedding_id = ?''', (vector_id,))
        result = c.fetchone()

        if result:
            return result[0]
        else:
            return None





def manage_for_index(url, pairs, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()

        for keyword, importance in pairs.items():
            c.execute('''SELECT importance FROM keyword_index WHERE keyword = ? AND url = ?''', (keyword, url))
            results = c.fetchall()

            if results:
                new_importance = results[0][0] + importance
                c.execute('''UPDATE keyword_index SET importance = ? WHERE keyword = ? AND url = ?''',
                          (new_importance, keyword, url))
            else:
                c.execute('INSERT INTO keyword_index (keyword, url, importance) VALUES (?, ?, ?)',
                          (keyword, url, importance))

        conn.commit()



def search_index(keywords, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        url_scores = {}

        for keyword in keywords:
            c.execute('''SELECT url, importance FROM keyword_index WHERE keyword = ?''', (keyword,))
            results = c.fetchall()

            for url, importance in results:
                url_scores[url] = url_scores.get(url, 0.0) + importance

        return url_scores

#below this line is the vector db

def initialize_vector_database(db_path='db/live1.db'):

    with open_db(db_path) as conn:
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS vectors
                     (id INT PRIMARY KEY,
                      dtype TEXT NOT NULL,
                      vector BLOB NOT NULL)''')


        conn.commit()

def add_vector(vector, id):
    with open_db(db_path='db/live1.db') as conn:
        vector = np.array(vector)
        new_vector = vector.tobytes()
        c = conn.cursor()

        c.execute('''INSERT INTO vectors (id, vector, dtype) VALUES (?, ?, ?)''', (id, new_vector, str(vector.dtype)))

        conn.commit()

def delete_vector(id):
    with open_db(db_path='db/live1.db') as conn:
        c = conn.cursor()
        c.execute('''DELETE FROM vectors WHERE id = ?''', (id,))
        conn.commit()

def get_vector(id):
    with open_db(db_path='db/live1.db') as conn:
        c = conn.cursor()
        c.execute('''SELECT vector FROM vectors WHERE id = ?''', (id,))
        vector = c.fetchone()
        return vector

def cosine_similarity_vectors(input_vector, top_k=50):
    with open_db(db_path='db/live1.db') as conn:
        res_map = {}
        c = conn.cursor()
        c.execute('''SELECT vector, id, dtype FROM vectors''')
        results = c.fetchall()
        for vector, id, dtype in results:
            if not isinstance(vector, bytes):
                raise TypeError(f"Expected bytes, got {type(vector)} for id {id}")
            vector = np.frombuffer(vector, dtype=dtype).reshape(384, 1).flatten()
            cosine = cosine_similarity(vector, input_vector).flatten()
            res_map[id] = float(cosine[0])
        sorted_dict = sorted(res_map.items(), key=lambda x: x[1], reverse=True)
        return sorted_dict[:top_k]

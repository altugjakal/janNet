import sqlite3
from contextlib import contextmanager
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
        c.execute('''INSERT OR IGNORE INTO urls (url) VALUES (?)''', (url,))
        conn.commit()


def is_url_visited(url, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM urls WHERE url = ?''', (url,))
        return c.fetchone() is not None




def add_to_queue(url, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO queue (url) VALUES (?)''', (url,))
        conn.commit()
def add_to_queue_batch(urls, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.executemany(
            '''INSERT OR IGNORE INTO queue (url) VALUES (?)''',
            [(url,) for url in urls]
        )
        conn.commit()

def get_total_kw_count(keyword, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT COUNT(*) FROM keyword_index WHERE keyword = ?''', (keyword,))
        return c.fetchone()[0]

def get_total_url_count(db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT COUNT(*) FROM urls''')
        return c.fetchone()[0]

def get_queue_size(db_path='db/jannet1.db'):
    """Get current queue size"""
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT COUNT(*) FROM queue''')
        return c.fetchone()[0]

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


def get_queue_batch(db_path='db/jannet1.db', limit=1000):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM queue ORDER BY added_at ASC LIMIT ?''',
                  (limit,))

        return c.fetchall()


def add_domain(domain, db_path='db/jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO domains (domain) VALUES (?, ?)''', (domain))
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

        updates = []
        inserts = []

        for keyword, importance in pairs.items():
            c.execute('''SELECT importance FROM keyword_index WHERE keyword = ? AND url = ?''', (keyword, url))
            result = c.fetchone()




            if result:
                new_importance = float(result[0]) + float(importance)
                updates.append((new_importance, keyword, url))

            else:
                inserts.append((keyword, url, float(importance)))

        if updates:
                c.executemany(
                    '''UPDATE keyword_index SET importance = ? WHERE keyword = ? AND url = ?''',
                    updates
                )
        if inserts:
                c.executemany(
                    '''INSERT INTO keyword_index (keyword, url, importance) VALUES (?, ?, ?)''',
                    inserts
                )

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


import sqlite3
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def open_db(db_path='jannet1.db'):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def initialize_database(db_path='jannet1.db'):
    """Run this once to create tables"""
    with open_db(db_path) as conn:
        c = conn.cursor()

        # URLs table
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

        # Create indexes for fast lookups
        c.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON keyword_index(keyword)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_url ON keyword_index(url)')

        conn.commit()


def add_url(url, db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO urls (url, crawled_at) VALUES (?, ?)''', (url, datetime.now()))
        conn.commit()


def is_url_visited(url, db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM urls WHERE url = ?''', (url,))
        return c.fetchone() is not None


def get_all_urls(db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM urls''')
        return c.fetchall()


def add_to_queue(url, db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO queue (url, added_at) VALUES (?, ?)''', (url, datetime.now()))
        conn.commit()


def drop_from_queue(url, db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''DELETE FROM queue WHERE url = ?''', (url,))
        conn.commit()


def is_in_queue(url, db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM queue WHERE url = ?''', (url,))
        return len(c.fetchall()) > 0


def get_queue(db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT url FROM queue''')
        return c.fetchall()


def add_domain(domain, db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO domains (domain, added_at) VALUES (?, ?)''', (domain, datetime.now()))
        conn.commit()


def check_domain(domain, db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT domain FROM domains WHERE domain = ?''', (domain,))
        return c.fetchone() is not None


def get_domains(db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT domain FROM domains''')
        return c.fetchall()


def manage_for_index(url, pairs, db_path='jannet1.db'):
    """Insert or update keyword importance values for a given URL."""
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


def search_index(keywords, db_path='jannet1.db'):
    with open_db(db_path) as conn:
        c = conn.cursor()
        url_scores = {}

        for keyword in keywords:
            c.execute('''SELECT url, importance FROM keyword_index WHERE keyword = ?''', (keyword,))
            results = c.fetchall()

            for url, importance in results:
                url_scores[url] = url_scores.get(url, 0.0) + importance

        return url_scores

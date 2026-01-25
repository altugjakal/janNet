import sqlite3
from contextlib import contextmanager


class IndexDB:
    def __init__(self):
        with self.open_db() as conn:
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
                          PRIMARY KEY (keyword, url))''')

            c.execute('''CREATE TABLE IF NOT EXISTS vector_index (
                id,
                embedding_id INTEGER NOT NULL,
                url TEXT,
                created_at TEXT NOT NULL default CURRENT_TIMESTAMP,
                PRIMARY KEY (id))''')

            # Create indexes for fast lookups
            c.execute('CREATE INDEX IF NOT EXISTS idx_keyword ON keyword_index(keyword)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_url ON keyword_index(url)')

            conn.commit()

    @contextmanager
    def open_db(self, db_path='db/general.db'):

        conn = sqlite3.connect(db_path)
        try:

            yield conn
        finally:
            conn.close()

    def add_url(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR IGNORE INTO urls (url) VALUES (?)''', (url,))
            conn.commit()

    def is_url_visited(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM urls WHERE url = ?''', (url,))
            return c.fetchone() is not None

    def add_to_queue(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR IGNORE INTO queue (url) VALUES (?)''', (url,))
            conn.commit()

    def add_to_queue_batch(self, urls):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany(
                '''INSERT OR IGNORE INTO queue (url) VALUES (?)''',
                [(url,) for url in urls]
            )
            conn.commit()

    def get_total_kw_count(self, keyword):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM keyword_index WHERE keyword = ?''', (keyword,))
            return c.fetchone()[0]

    def get_total_url_count(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM urls''')
            return c.fetchone()[0]

    def get_queue_size(self):
        """Get current queue size"""
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM queue''')
            return c.fetchone()[0]

    def drop_from_queue(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''DELETE FROM queue WHERE url = ?''', (url,))
            conn.commit()

    def is_in_queue(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM queue WHERE url = ?''', (url,))
            return len(c.fetchall()) > 0

    def get_queue_batch(self, limit=1000):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM queue ORDER BY added_at ASC LIMIT ?''',
                      (limit,))

            return c.fetchall()

    def add_domain(self, domain):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR IGNORE INTO domains (domain) VALUES (?, ?)''', (domain))
            conn.commit()

    def check_domain(self, domain):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT domain FROM domains WHERE domain = ?''', (domain,))
            return c.fetchone() is not None

    def get_domains(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT domain FROM domains''')
            return c.fetchall()

    def manage_vector_for_index(self, url, emb_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO vector_index (embedding_id,
                    url) VALUES (?, ?)''', (emb_id, url))
            conn.commit()

    def get_url_by_vector_id(self, vector_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM vector_index WHERE embedding_id = ?''', (vector_id,))
            result = c.fetchone()

            if result:
                return result[0]
            else:
                return None

    def manage_for_index(self, url, keywords):
        with self.open_db() as conn:
            c = conn.cursor()

            c.executemany(
                    '''INSERT OR IGNORE INTO keyword_index (url, keyword) VALUES (?, ?)''',
                    [(url, keyword) for keyword in keywords]
                )

            conn.commit()

    def search_index(self, keywords):
        with self.open_db() as conn:
            c = conn.cursor()
            results = []

            for keyword in keywords:
                c.execute('''SELECT url, keyword FROM keyword_index WHERE keyword = ?''', (keyword,))
                results += c.fetchall()

            return results


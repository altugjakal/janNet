import sqlite3
from contextlib import contextmanager
from core.db.thread_lock_wrapper import locked

class IndexDB:
    def __init__(self):
        with self.open_db() as conn:
            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS urls
                         (url TEXT PRIMARY KEY,
                         content TEXT NOT NULL,
                          crawled_at TIMESTAMP NOT NULL default CURRENT_TIMESTAMP)''')

            # Queue table
            c.execute('''CREATE TABLE IF NOT EXISTS queue
                         (url TEXT PRIMARY KEY,
                         issuer_thread_id INTEGER NOT NULL,
                          added_at TIMESTAMP NOT NULL default CURRENT_TIMESTAMP)''')

            # Domains table
            c.execute('''CREATE TABLE IF NOT EXISTS domains
                         (domain TEXT PRIMARY KEY,
                          added_at TIMESTAMP NOT NULL default CURRENT_TIMESTAMP)''')

            # Keyword index table
            c.execute('''CREATE TABLE IF NOT EXISTS keyword_index
                         (keyword TEXT,
                          url TEXT,
                          score INTEGER NOT NULL default 0,
                          PRIMARY KEY (keyword))''')

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
    def open_db(self, db_path="db/general.db"):

        conn = sqlite3.connect(db_path)
        try:

            yield conn
        finally:
            conn.close()

    @locked
    def add_url(self, url, content):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR IGNORE INTO urls (url, content) VALUES (?, ?)''', (url, content))
            conn.commit()

    @locked
    def is_url_visited(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM urls WHERE url = ?''', (url,))
            return c.fetchone() is not None

    @locked
    def add_to_queue(self, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR IGNORE INTO queue (url, issuer_thread_id) VALUES (?, ?)''', (url, thread_id))
            conn.commit()

    @locked
    def add_to_queue_batch(self, urls, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany(
                '''INSERT OR IGNORE INTO queue (url, issuer_thread_id) VALUES (?, ?)''',
                [(url, thread_id) for url in urls]
            )
            conn.commit()


    @locked
    def get_total_kw_count(self, keyword):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM keyword_index WHERE keyword = ?''', (keyword,))
            return c.fetchone()[0]


    @locked
    def get_total_url_count(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM urls''')
            return c.fetchone()[0]


    @locked
    def get_queue_size(self, thread_id):
        """Get current queue size"""
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM queue WHERE issuer_thread_id = ? ''', (thread_id,))
            return c.fetchone()[0]

    @locked
    def drop_from_queue(self, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''DELETE FROM queue WHERE url = ? AND issuer_thread_id = ?''', (url, thread_id))
            conn.commit()

    @locked
    def is_in_queue(self, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM queue WHERE url = ? AND issuer_thread_id = ?''', (url, thread_id))
            return len(c.fetchall()) > 0

    @locked
    def get_queue_batch(self, thread_id, limit=1000):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM queue WHERE issuer_thread_id = ? ORDER BY added_at ASC LIMIT ?''',
                      (thread_id, limit))

            return c.fetchall()

    @locked
    def add_domain(self, domain):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT OR IGNORE INTO domains (domain) VALUES (?, ?)''', (domain))
            conn.commit()

    @locked
    def check_domain(self, domain):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT domain FROM domains WHERE domain = ?''', (domain,))
            return c.fetchone() is not None

    @locked
    def get_domains(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT domain FROM domains''')
            return c.fetchall()

    @locked
    def manage_vector_for_index(self, url, emb_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO vector_index (embedding_id,
                    url) VALUES (?, ?)''', (emb_id, url))
            conn.commit()

    @locked
    def get_url_by_vector_id(self, vector_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT vector_index.url, urls.content FROM vector_index LEFT JOIN urls ON vector_index.url = 
            urls.url WHERE embedding_id = ?''', (vector_id,))
            result = c.fetchone()


            return result

    @locked
    def manage_for_index(self, url, pairs):
        with self.open_db() as conn:
            c = conn.cursor()

            c.executemany(
                    '''INSERT OR IGNORE INTO keyword_index (url, keyword, score) VALUES (?, ?, ?)''',
                    [(url, keyword, score) for keyword, score in pairs.items()]
                )

            conn.commit()

    @locked
    def search_index(self, keywords, limit):
        with self.open_db() as conn:
            c = conn.cursor()
            results = []

            for keyword in keywords:
                c.execute('''SELECT keyword_index.url, keyword_index.keyword, urls.content, keyword_index.score FROM keyword_index LEFT JOIN urls ON urls.url = keyword_index.url WHERE keyword = ? ORDER BY keyword_index.score LIMIT ?''', (keyword, limit))
                results += c.fetchall()

            return results


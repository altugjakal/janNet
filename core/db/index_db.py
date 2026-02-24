import mysql.connector
from contextlib import contextmanager
from utils.thread_lock_wrapper import locked


class IndexDB:
    def __init__(self, host, user, password, database, port):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port
        }
        with self.open_db() as conn:
            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS urls
                         (url VARCHAR(2048),
                        url_hash CHAR(64) AS (SHA2(url, 256)) STORED PRIMARY KEY,
                         content LONGTEXT NOT NULL,
                          crawled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

            c.execute('''CREATE TABLE IF NOT EXISTS queue
            
                         (url VARCHAR(2048),
                         url_hash CHAR(64) AS (SHA2(url, 256)) STORED PRIMARY KEY,
                         issuer_thread_id INTEGER NOT NULL,
                          added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

            c.execute('''CREATE TABLE IF NOT EXISTS domains
                         (domain VARCHAR(512) PRIMARY KEY,
                          added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

            c.execute('''CREATE TABLE IF NOT EXISTS keyword_index
                         (keyword VARCHAR(512),
                          url VARCHAR(2048),
                          url_hash CHAR(64) AS (SHA2(url, 256)) STORED,
                          score INTEGER NOT NULL DEFAULT 0,
                          PRIMARY KEY (keyword, url_hash))''')

            c.execute('''CREATE TABLE IF NOT EXISTS vector_index (
                id INTEGER AUTO_INCREMENT PRIMARY KEY,
                embedding_id INTEGER NOT NULL,
                url VARCHAR(2048),
                url_hash CHAR(64) AS (SHA2(url, 256)) STORED,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')


            try:
                c.execute('CREATE INDEX idx_url_hash ON keyword_index(url_hash)')
                c.execute('CREATE INDEX idx_queue_url ON queue(url)')
                c.execute('CREATE INDEX idx_keyword ON keyword_index(keyword)')
            except mysql.connector.errors.DatabaseError:
                pass



            conn.commit()

    @contextmanager
    def open_db(self):
        conn = mysql.connector.connect(**self.config)
        try:
            yield conn
        finally:
            conn.close()

    @locked
    def add_url(self, url, content):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT IGNORE INTO urls (url, content) VALUES (%s, %s)''', (url, content))
            conn.commit()

    @locked
    def is_url_visited(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM urls WHERE url_hash = SHA2(%s, 256)''', (url,))
            return c.fetchone() is not None

    @locked
    def add_to_queue(self, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT IGNORE INTO queue (url, issuer_thread_id) VALUES (%s, %s)''', (url, thread_id))
            conn.commit()

    @locked
    def add_to_queue_batch(self, urls, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany(
                '''INSERT IGNORE INTO queue (url, issuer_thread_id) VALUES (%s, %s)''',
                [(url, thread_id) for url in urls]
            )
            conn.commit()

    @locked
    def get_total_kw_count(self, keyword):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM keyword_index WHERE keyword = %s''', (keyword,))
            return c.fetchone()[0]

    @locked
    def get_total_url_count(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM urls''')
            return c.fetchone()[0]

    @locked
    def get_queue_size(self, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM queue WHERE issuer_thread_id = %s''', (thread_id,))
            return c.fetchone()[0]

    @locked
    def drop_from_queue(self, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''DELETE FROM queue WHERE url_hash = SHA2(%s, 256) AND issuer_thread_id = %s''', (url, thread_id))
            conn.commit()

    @locked
    def is_in_queue(self, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM queue WHERE url_hash = SHA2(%s, 256) AND issuer_thread_id = %s''', (url, thread_id))
            return c.fetchone() is not None

    @locked
    def get_queue_batch(self, thread_id, limit=1000):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM queue WHERE issuer_thread_id = %s ORDER BY added_at ASC LIMIT %s''',
                      (thread_id, limit))
            return c.fetchall()

    @locked
    def add_domain(self, domain):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT IGNORE INTO domains (domain) VALUES (%s)''', (domain,))
            conn.commit()

    @locked
    def check_domain(self, domain):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT domain FROM domains WHERE domain = %s''', (domain,))
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
            c.execute('''INSERT INTO vector_index (embedding_id, url) VALUES (%s, %s)''', (emb_id, url))
            conn.commit()

    @locked
    def get_url_by_vector_id(self, vector_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT vector_index.url, urls.content FROM vector_index 
                         LEFT JOIN urls ON vector_index.url_hash = urls.url_hash
                         WHERE embedding_id = %s''', (vector_id,))
            return c.fetchone()

    @locked
    def manage_for_index(self, url, pairs):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany(
                '''INSERT INTO keyword_index (url, keyword, score) VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE score = score + VALUES(score)''',
                [(url, keyword, score) for keyword, score in pairs.items()]
            )
            conn.commit()

    @locked
    def manage_for_index_batch(self, tuples):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany(
                '''INSERT INTO keyword_index (url, keyword, score) VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE score = score + VALUES(score)''',
                tuples
            )
            conn.commit()

    @locked
    def search_index(self, keywords, limit):
        with self.open_db() as conn:
            c = conn.cursor()
            placeholders = ','.join(['%s'] * len(keywords))
            query = f''' SELECT keyword_index.url, keyword_index.keyword, urls.content, keyword_index.score
                    FROM keyword_index
                    LEFT JOIN urls ON urls.url_hash = keyword_index.url_hash
                    WHERE keyword_index.keyword IN ({placeholders}) ORDER BY keyword_index.score DESC
                        LIMIT %s'''
            c.execute(query, (*keywords, limit))
            return c.fetchall()

    @locked
    def get_content_by_url(self, url, limit):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT content FROM urls WHERE url = %s LIMIT %s''', (url, limit))
            return c.fetchone()
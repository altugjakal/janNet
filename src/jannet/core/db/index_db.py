import mysql.connector
from contextlib import contextmanager
from src.jannet.utils.thread_lock_wrapper import locked


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
                         (id INTEGER PRIMARY KEY,
                         url VARCHAR(2048),
                        url_hash CHAR(64) AS (SHA2(url, 256)) STORED ,
                         content LONGTEXT NOT NULL,
                         processed BOOLEAN NOT NULL DEFAULT 0,
                          crawled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

            c.execute('''CREATE TABLE IF NOT EXISTS link_graph (
            from_url_id INT,
            to_url_id INT,
            crawled_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (from_url_id, to_url_id)
            )''')

            c.execute('''CREATE TABLE IF NOT EXISTS pagerank_scores (
                         id INTEGER NOT NULL PRIMARY KEY,
                         score INTEGER NOT NULL DEFAULT 0,
                         added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)
                
            
            ''')

            c.execute('''CREATE TABLE IF NOT EXISTS queue
            
                         (url VARCHAR(2048),
                         url_hash CHAR(64) AS (SHA2(url, 256)) STORED,
                         id INTEGER NOT NULL PRIMARY KEY,
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
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    @locked
    def add_url(self, id, url, content):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT IGNORE INTO urls (id, url, content) VALUES (%s, %s, %s)''', (id, url, content))
            conn.commit()


    def mark_url_as_processed(self, id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute(
                '''UPDATE urls SET processed = 1 WHERE id = %s''', (id,))
            conn.commit()

    @locked
    def get_process_queue_next(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url, content, id FROM urls WHERE processed = 0 LIMIT 1''', ())
            return c.fetchone()



    @locked
    def is_url_visited(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM urls WHERE url_hash = SHA2(%s, 256)''', (url,))
            return c.fetchone() is not None

    @locked
    def add_to_queue(self, id, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT IGNORE INTO queue (id, url, issuer_thread_id) VALUES (%s, %s, %s)''', (id, url, thread_id))
            conn.commit()

    @locked
    def add_to_queue_batch(self, pairs, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany(
                '''INSERT IGNORE INTO queue (id, url, issuer_thread_id) VALUES (%s, %s, %s)''',
                [(id, url, thread_id) for id, url in pairs]
            )
            conn.commit()

    @locked
    def get_total_kw_count(self, keyword):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM keyword_index WHERE keyword = %s''', (keyword,))
            return c.fetchone()[0]

    @locked
    def get_total_kw_count_batch(self, keywords):
        with self.open_db() as conn:
            r_map = {}
            placeholders = ', '.join(['%s'] * len(keywords))
            c = conn.cursor()
            c.execute(
                f'''SELECT COUNT(*), keyword FROM keyword_index WHERE keyword IN ({ placeholders }) GROUP BY keyword''', tuple(keywords))
            results = c.fetchall()
            for keyword in keywords:
                r_map[keyword] = 0

            for count, keyword in results:
                r_map[keyword] = count

        return r_map

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
    def get_queue_next(self, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url, id FROM queue WHERE issuer_thread_id = %s ORDER BY added_at ASC LIMIT 1''',
                      (thread_id,))
            return c.fetchone()
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
    def manage_vector_for_index_batch(self, pairs):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany('''INSERT INTO vector_index (embedding_id, url) VALUES (%s, %s)''', pairs)
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
    def get_url_by_vector_id_batch(self, vector_ids):
        with self.open_db() as conn:
            urls = []
            contents = []
            ids = []
            placeholders = ', '.join(['%s'] * len(vector_ids))
            c = conn.cursor()
            c.execute(f'''SELECT embedding_id, vector_index.url, urls.content FROM vector_index 
                         LEFT JOIN urls ON vector_index.url_hash = urls.url_hash
                         WHERE embedding_id IN({ placeholders })''', tuple(vector_ids))
            results = c.fetchall()
            for id, url, content in results:
                ids.append(id)
                urls.append(url)
                contents.append(content)

            return ids, urls, contents

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
            query = f''' SELECT 
    keyword_index.url, 
    keyword_index.keyword, 
    urls.content, 
    keyword_index.score
FROM keyword_index
LEFT JOIN urls ON urls.url_hash = keyword_index.url_hash
WHERE keyword_index.keyword IN ({placeholders})
ORDER BY 
    COUNT(*) OVER (PARTITION BY keyword_index.url) DESC,
    keyword_index.score DESC
LIMIT %s'''
            c.execute(query, (*keywords, limit))
            return c.fetchall()

    @locked
    def get_content_by_url(self, url, limit):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT content FROM urls WHERE url = %s LIMIT %s''', (url, limit))
            return c.fetchone()

    @locked
    def add_link_relation_batch(self, pairs):
        with self.open_db() as conn:
            pairs = list(pairs)
            c = conn.cursor()
            c.executemany(
                '''INSERT INTO link_graph (to_url_id, from_url_id) VALUES (%s, %s)''',
            pairs
            )
            conn.commit()


    def get_all_link_relation(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT to_url_id, from_url_id FROM link_graph''')
            return c.fetchall()

    def update_pagerank_batch(self, pairs):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany(
                '''INSERT IGNORE INTO pagerank_scores (id, score) VALUES (%s, %s)''', pairs
            )
            conn.commit()
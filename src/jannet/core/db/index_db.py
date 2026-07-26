import traceback

import mysql.connector
from contextlib import contextmanager
from src.jannet.utils.thread_lock_wrapper import db_locked


class IndexDB:
    def __init__(self, host, user, password, database, port):

        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port
        }
        self.conn = mysql.connector.connect(**self.config)
        with self.open_db() as conn:
            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS urls
                         (id INTEGER PRIMARY KEY,
                         url VARCHAR(2048),
                        url_hash CHAR(64) AS (SHA2(url, 256)) STORED ,
                         content LONGTEXT NOT NULL,
                        content_length INTEGER NOT NULL,
                         processed BOOLEAN NOT NULL DEFAULT 0,
                          crawled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

            c.execute('''CREATE TABLE IF NOT EXISTS link_graph (
    id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    from_url_id INTEGER,
    to_url_id INTEGER,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''')

            c.execute('''CREATE TABLE IF NOT EXISTS pagerank_scores (
                         id INTEGER NOT NULL PRIMARY KEY,
                         score DOUBLE NOT NULL,
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

            c.execute('''CREATE TABLE IF NOT EXISTS vector_index (
                            id INTEGER NOT NULL,
                            embedding_id INTEGER NOT NULL,
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (id, embedding_id)
                         )''')


            try:
                c.execute('CREATE INDEX idx_queue_url_hash ON queue(url_hash);')

                c.execute('CREATE INDEX idx_urls_url_hash ON urls(url_hash);')

                c.execute('CREATE INDEX idx_urls_url ON urls(url);')

                c.execute('CREATE INDEX idx_urls_id ON urls(id);')

                c.execute('CREATE INDEX idx_vector_id ON vector_index(id);')





            except mysql.connector.errors.DatabaseError:
                pass



            conn.commit()

    @contextmanager
    def open_db(self):
        conn = self.conn
        try:
            conn.ping(reconnect=True)
            yield conn
        except mysql.connector.Error as e:
            conn.rollback()
            traceback.print_exc()
            raise

    @db_locked
    def add_url(self, id, url, content):
        with self.open_db() as conn:
            c = conn.cursor()

            c.execute('''INSERT INTO urls (id, url, content, content_length) VALUES (%s, %s, %s, %s)''', (id, url, content, len(content.split())))
            conn.commit()

    @db_locked
    def mark_url_as_processed(self, id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute(
                '''UPDATE urls SET processed = 1 WHERE id = %s''', (id,))
            conn.commit()

    @db_locked
    def get_process_queue(self, limit):
        with self.open_db() as conn:
            c = conn.cursor()

            c.execute('SELECT id FROM urls WHERE processed = 0 LIMIT %s FOR UPDATE SKIP LOCKED', (limit,))
            ids = [row[0] for row in c.fetchall()]

            if not ids:
                return []

            placeholders = ','.join(['%s'] * len(ids))

            c.execute(f'SELECT url, content, id FROM urls WHERE id IN ({placeholders})', tuple(ids))
            results = c.fetchall()

            c.execute(f'UPDATE urls SET processed = 2 WHERE id IN ({placeholders})', tuple(ids))

            conn.commit()
            return results

    @db_locked
    def is_url_visited(self, url):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM urls WHERE url_hash = SHA2(%s, 256)''', (url,))
            return c.fetchone() is not None


    @db_locked
    def add_to_queue(self, id, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT IGNORE INTO queue (id, url, issuer_thread_id) VALUES (%s, %s, %s)''', (id, url, thread_id))
            conn.commit()

    @db_locked
    def add_to_queue_batch(self, pairs, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany(
                '''INSERT IGNORE INTO queue (id, url, issuer_thread_id) VALUES (%s, %s, %s)''',
                [(id, url, thread_id) for id, url in pairs]
            )
            conn.commit()




    @db_locked
    def get_total_url_count(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM urls''')
            return c.fetchone()[0]

    @db_locked
    def get_queue_size(self, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM queue WHERE issuer_thread_id = %s''', (thread_id,))
            return c.fetchone()[0]

    @db_locked
    def drop_from_queue(self, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''DELETE FROM queue WHERE url_hash = SHA2(%s, 256) AND issuer_thread_id = %s''', (url, thread_id))
            conn.commit()

    @db_locked
    def is_in_queue(self, url, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url FROM queue WHERE url_hash = SHA2(%s, 256) AND issuer_thread_id = %s''', (url, thread_id))
            return c.fetchone() is not None

    @db_locked
    def get_queue_next(self, thread_id):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT url, id FROM queue WHERE issuer_thread_id = %s ORDER BY added_at ASC LIMIT 1''',
                      (thread_id,))

            result = c.fetchone()
            conn.commit()
            return result if result else []
    @db_locked
    def add_domain(self, domain):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''INSERT IGNORE INTO domains (domain) VALUES (%s)''', (domain,))
            conn.commit()

    @db_locked
    def check_domain(self, domain):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT domain FROM domains WHERE domain = %s''', (domain,))
            return c.fetchone() is not None

    @db_locked
    def get_domains(self):
        with self.open_db() as conn:
            c = conn.cursor()
            c.execute('''SELECT domain FROM domains''')
            return c.fetchall()


    @db_locked
    def manage_vector_for_index_batch(self, pairs):
        with self.open_db() as conn:
            c = conn.cursor()
            c.executemany('''INSERT INTO vector_index (id, embedding_id) VALUES (%s, %s)''', pairs)
            conn.commit()


    @db_locked
    def get_id_by_vector_id_batch(self, vector_ids):
        with self.open_db() as conn:
            ids = []
            contents = []
            emb_ids = []
            placeholders = ', '.join(['%s'] * len(vector_ids))
            if not placeholders:
                return emb_ids, ids, contents
            c = conn.cursor()
            c.execute(f'''SELECT embedding_id, vector_index.id, urls.content 
                         FROM vector_index 
                         LEFT JOIN urls ON vector_index.id = urls.id
                         WHERE embedding_id IN ({placeholders})''', vector_ids)
            results = c.fetchall()
            for emb_id, id, content in results:
                emb_ids.append(emb_id)
                ids.append(id)
                contents.append(content)

            return emb_ids, ids, contents






    @db_locked
    def get_contents_by_ids(self, ids):
        with self.open_db() as conn:
            c = conn.cursor()

            placeholders = ', '.join(['%s'] * len(ids))
            query = f'''SELECT id, content FROM urls WHERE id IN ({placeholders})'''

            c.execute(query, list(ids))

            return dict(c.fetchall())

    @db_locked
    def get_content_lengths_by_ids(self, ids):
        with self.open_db() as conn:
            c = conn.cursor()

            placeholders = ', '.join(['%s'] * len(ids))
            query = f'''SELECT id, content_length FROM urls WHERE id IN ({placeholders})'''

            c.execute(query, list(ids))

            return dict(c.fetchall())

    @db_locked
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
                '''INSERT INTO pagerank_scores (id, score) VALUES (%s, %s) ''', pairs
            )
            conn.commit()

    def get_pagerank_scores_batch(self, ids):
        with self.open_db() as conn:
            c = conn.cursor()
            placeholders = ','.join(['%s'] * len(ids))
            s_map = {id: 0 for id in ids}

            try:
                c.execute(
                    f'''SELECT urls.id, pagerank_scores.score
                FROM urls
                         LEFT JOIN pagerank_scores ON pagerank_scores.id = urls.id
                WHERE urls.id IN ({ placeholders })''', tuple(ids)
                )

                results = c.fetchall()
            except Exception as e:
                traceback.print_exc()
            for id, pagerank_score in results:

                s_map[id] = pagerank_score if pagerank_score else 0


            return s_map


    def get_url_from_ids(self, ids):
        placeholders = ', '.join(['%s'] * len(ids))

        with self.open_db() as conn:
            c = conn.cursor()

            c.execute(f'''SELECT id, url FROM urls WHERE id IN ({placeholders})''', tuple(ids))
            return c.fetchall()

    @db_locked
    def destroy_all_data(self):

        tables = [
            "vector_index",
            "domains",
            "queue",
            "pagerank_scores",
            "link_graph",
            "urls"
        ]

        with self.open_db() as conn:
            c = conn.cursor()

            c.execute("SET FOREIGN_KEY_CHECKS = 0;")

            for table in tables:
                c.execute(f"DROP TABLE IF EXISTS {table};")

            c.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()

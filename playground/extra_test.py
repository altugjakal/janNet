from src.jannet.managers.db_manager import get_db

db = get_db()
open_db = db.open_db

with open_db() as conn:
    c = conn.cursor()
    c.execute('''SELECT url, processed FROM urls''')
    results = c.fetchall()
    print(results)

    print(db.get_process_queue_next())

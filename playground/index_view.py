from src.jannet.managers.db_manager import get_db

db = get_db()


db.destroy_all_data()
print('done')

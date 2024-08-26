from services.db_service import DBService

db_service = DBService(
    host='localhost',
    user='root',
    password='root',
    database='naukri_user_db'
)

db_service.create_users_table()
import re
import mysql.connector

class DBService:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()
    def validate_email(self, email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(pattern, email):
            return True
        else:
            return False
        
    def close_connection(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        self.conn.commit()

    def check_login(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()
        if result:
            return True
        else:
            return False

    def register_user(self, username, password, email):
        if not self.validate_email(email):
            print("Invalid email address")
            return False
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(query, (username, password, email))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    def get_user(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return result

    def create_users_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL
            )
        ''')
        self.conn.commit()

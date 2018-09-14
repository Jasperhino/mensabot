import mysql.connector

class DBHelper:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="jasperoo",
            passwd="sN312:WZZi2QZcUZkIF-",
            database="jasperoo"
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("SHOW TABLES")
        

    def setup(self):
        print("creating table")
        stmt = "CREATE TABLE IF NOT EXISTS chats (chat_id UNIQUE)"
        self.cursor.execute(stmt)
        self.conn.commit()

    def add_entry(self, chat_id):
        stmt = "INSERT INTO chats(chat_id) SELECT (?) WHERE NOT EXISTS (SELECT chat_id FROM chats WHERE chat_id == (?))"
        args = (chat_id, chat_id)
        self.cursor.execute(stmt, args)
        self.conn.commit()
    

    def delete_entry(self, chat_id):
        stmt = "DELETE FROM chats WHERE chat_id = (?)"
        args = (chat_id,)
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def delete_all(self):
        stmt = "DELETE FROM chats"
        self.cursor.execute(stmt)
        self.conn.commit()

    def delete_db(self):
        stmt = "DROP TABLE chats"
        self.cursor.execute(stmt)
        self.conn.commit()

    def get_all_chats(self):
        stmt = "SELECT chat_id FROM chats"
        self.cursor.execute(stmt)
        return self.cursor.fetchall()
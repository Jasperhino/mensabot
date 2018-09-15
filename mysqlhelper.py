import mysql.connector

class DBHelper:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="" #sN312:WZZi2QZcUZkIF-
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS jasperoo")
        self.conn.close()
        
    def setup(self):
        print("creating table")
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="", #sN312:WZZi2QZcUZkIF-
            database="jasperoo"
        )
        self.cursor = self.conn.cursor()

        stmt = "CREATE TABLE IF NOT EXISTS chats (chat_id INT NOT NULL PRIMARY KEY);"
        self.cursor.execute(stmt)
        self.conn.commit()

    def add_entry(self, chat_id):
        print("add_entry")
        stmt = "INSERT INTO chats(chat_id) SELECT %s WHERE NOT EXISTS (SELECT chat_id FROM chats WHERE chat_id = %s)"
        args = (chat_id, chat_id)
        self.cursor.execute(stmt, args)
        self.conn.commit()
    

    def delete_entry(self, chat_id):
        stmt = "DELETE FROM chats WHERE chat_id = %s"
        args = (chat_id,)
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def delete_all(self):
        stmt = "DELETE FROM chats"
        self.cursor.execute(stmt)
        self.conn.commit()

    def get_all_chats(self):
        stmt = "SELECT chat_id FROM chats"
        self.cursor.execute(stmt)
        return [x[0] for x in self.cursor.fetchall()]
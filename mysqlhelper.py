import mysql.connector

class DBHelper:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="jasperoo",
            passwd="XHVSszwjz_n0pEkqX7-1"
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS jasperoo")
        self.conn.close()
    
    def setup(self):
        print("Setting up Database...")
        self.conn = mysql.connector.connect(
            host="localhost",
            user="jasperoo",
            passwd="XHVSszwjz_n0pEkqX7-1",
            database="jasperoo"
        )
        self.cursor = self.conn.cursor()

        stmt = "CREATE TABLE IF NOT EXISTS chats (chat_id INT NOT NULL PRIMARY KEY, listening BOOLEAN NOT NULL, time CHARACTER(5));"
        self.cursor.execute(stmt)
        self.conn.commit()

    def add_entry(self, chat_id):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        print("add_entry")
        stmt = "INSERT INTO chats(chat_id, listening, time) VALUES (%s, 1, '10:45')"
        args = (chat_id,)
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def contains(self, chat_id):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        stmt = "SELECT * FROM chats WHERE chat_id = %s"
        args = (chat_id,)
        self.cursor.execute(stmt, args)
        return len(self.cursor.fetchall()) != 0

    def update_listening(self, chat_id, val):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        print("update_entry")
        stmt = "UPDATE chats SET listening = %s WHERE chat_id = %s"
        args = (val, chat_id)
        self.cursor.execute(stmt, args)
        self.conn.commit()
    
    def update_time(self, chat_id, val):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        print("update_entry")
        stmt = "UPDATE chats SET time = %s WHERE chat_id = %s"
        args = (val, chat_id)
        self.cursor.execute(stmt, args)
        self.conn.commit()

    def delete_entry(self, chat_id):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        stmt = "DELETE FROM chats WHERE chat_id = %s"
        args = (chat_id,)
        self.cursor.execute(stmt, args)
        self.conn.commit() 

    def delete_all(self):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        stmt = "DROP TABLE chats"
        self.cursor.execute(stmt)
        self.conn.commit()

    def get_all_chats(self):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        stmt = "SELECT chat_id FROM chats"
        self.cursor.execute(stmt)
        return [x[0] for x in self.cursor.fetchall()]

    def get_all_listeners(self):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        stmt = "SELECT chat_id, time FROM chats WHERE listening = 1"
        self.cursor.execute(stmt)
        return [(x[0], x[1]) for x in self.cursor.fetchall()]

    def get_time(self, chat_id):
        self.conn.ping(reconnect=True, attempts=1, delay=0)
        stmt = "SELECT time FROM chats WHERE chat_id = %s"
        args = (chat_id,)
        self.cursor.execute(stmt, args)
        return self.cursor.fetchone()[0]
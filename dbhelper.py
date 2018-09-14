import sqlite3

class DBHelper:
    def __init__(self, dbname="mensabot.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        print("creating table")
        stmt = "CREATE TABLE IF NOT EXISTS chats (chat_id UNIQUE)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_entry(self, chat_id):
        stmt = "INSERT INTO chats(chat_id) SELECT (?) WHERE NOT EXISTS (SELECT chat_id FROM chats WHERE chat_id == (?))"
        args = (chat_id, chat_id)
        self.conn.execute(stmt, args)
        self.conn.commit()
    

    def delete_entry(self, chat_id):
        stmt = "DELETE FROM chats WHERE chat_id = (?)"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_all(self):
        stmt = "DELETE FROM chats"
        self.conn.execute(stmt)
        self.conn.commit()

    def delete_db(self):
        stmt = "DROP TABLE chats"
        self.conn.execute(stmt)
        self.conn.commit()

    def get_all_chats(self):
        stmt = "SELECT chat_id FROM chats"
        return [x[0] for x in self.conn.execute(stmt)]
import sqlite3

class DBSetup:

    def __init__(self, dbname="bttn.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.c = self.conn.cursor()

    def setup(self):
        with self.conn:
            self.c.execute("""CREATE TABLE users (
                discord_id integer unique, 
                name text, 
                score integer, 
                status integer
                )""")
            
            self.c.execute("""CREATE TABLE bttns (
                discord_id integer, 
                party_name text, 
                timestamp real,
                foreign key(discord_id) references users(discord_id)
                )""")


db = DBSetup()
db.setup()
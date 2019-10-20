import sqlite3


class DBSetup:

    def __init__(self, dbname="bttn.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.c = self.conn.cursor()

    def setup(self):
        with self.conn:
            self.c.execute("""CREATE TABLE IF NOT EXISTS users (
                discord_id integer unique, 
                name text, 
                score integer, 
                status integer
                )""")

            self.c.execute("""CREATE TABLE IF NOT EXISTS bttns (
                discord_id integer, 
                party_name text, 
                timestamp real,
                foreign key(discord_id) references users(discord_id)
                )""")

            self.c.execute(""" CREATE TABLE IF NOT EXISTS telegram_users (
                telegram_id integer unique,
                discord_id integer,
                name text,
                score integer, 
                status integer,
                foreign key(discord_id) references users(discord_id)
                )""")

            self.c.execute("""CREATE TABLE IF NOT EXISTS telegram_btts (
                telegram_id integer, 
                party_name text, 
                timestamp real,
                foreign key(telegram_id) references telegram_users(telegram_id)
                )""")


db = DBSetup()
db.setup()

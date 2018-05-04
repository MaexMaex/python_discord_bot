import sqlite3
from sqlite_models import User, Bttn

class DBView:

    def __init__(self, dbname="bttn.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.c = self.conn.cursor()


    def is_not_drinking(self, discord_id):
        with self.conn:
            self.c.execute("SELECT status FROM users WHERE discord_id = :discord_id", {'discord_id': discord_id})
            if self.c.fetchone() is 0:
                return True


    def get_discord_id(self, discord_id):
        with self.conn:
            self.c.execute("SELECT discord_id FROM users WHERE discord_id = :discord_id", {'discord_id': discord_id})
            return self.c.fetchone()

    # add a user to the database
    def add_user(self, user):
        with self.conn:
            self.c.execute("INSERT INTO users VALUES (:discord_id, :name, :score, :status)", {'discord_id': user.discord_id, 'name': user.name, 'score': user.score, 'status': user.status})


    # updatea nick in the database
    def update_nickname(self, user):
        with self.conn:
            self.c.execute("UPDATE users SET name = :name WHERE discord_id = :discord_id", {'discord_id': user.discord_id, 'name': user.name})

    # fetch user.id
    def get_user(self, discord_id):
        with self.conn:
            self.c.execute("SELECT * FROM users WHERE discord_id = :discord_id", {'discord_id': discord_id})
            return self.c.fetchone()


    # adds a bttn for a user.id
    def add_score(self, user):
        with self.conn:
            self.c.execute("""UPDATE users SET score = score + 1
                    WHERE discord_id = :discord_id""",
                    {'discord_id': user.discord_id})

    #removes a bttn for a user
    def remove_score(self, user):
        with self.conn:
            self.c.execute("""UPDATE users SET score = score - 1
                    WHERE discord_id = :discord_id""",
                    {'discord_id': user.discord_id})
    
    #sets a stat for a user, used for manual db edits
    def edit_score(self, user, score):
        with self.conn:
            self.c.execute("""UPDATE users SET score = :score
                    WHERE discord_id = :discord_id""",
                    {'discord_id': user.discord_id, 'score': score})

    # get status for user.id
    def get_status(self, user):
        with self.conn:
            self.c.execute("SELECT status FROM users WHERE discord_id = :discord_id", {'discord_id': user.discord_id})
            return self.c.fetchone()

    # change the status of a user.id (/mystatus)
    def edit_status(self, user, status):
        with self.conn:
            self.c.execute("""UPDATE users SET status = :status
                    WHERE discord_id = :discord_id""",
                    {'discord_id': user.discord_id, 'status': status})

    # returns the statistics of the user.id (/myscore)
    def get_score(self, user):
        with self.conn:
            self.c.execute("SELECT score FROM users WHERE discord_id = :discord_id", {'discord_id': user.discord_id})
            return self.c.fetchone()

    #returns a the status for all users (/status)
    def get_all_status(self):
        with self.conn:
            self.c.execute("SELECT name, status FROM users")
            return self.c.fetchall()

    #returns the statistics for all users in the database (/score)
    def get_all_score(self):
        with self.conn:
            self.c.execute("SELECT name, score FROM users ORDER BY score DESC")
            return self.c.fetchall()

    # add event to the bttn table
    def add_bttn(self, user, bttn):
        with self.conn:
            self.c.execute("INSERT INTO bttns VALUES (:discord_id, :party_name, :timestamp)", {'discord_id': user.discord_id, 'party_name': bttn.party_name, 'timestamp': bttn.timestamp})
               
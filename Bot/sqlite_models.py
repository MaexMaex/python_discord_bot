class User:
        
    def __init__(self, discord_id, name, score=0, status=0):
        self.discord_id = discord_id
        self.name = name
        self.score = score
        self.status = status

    def __repr__(self):
        return self.name

class Bttn():

    def __init__(self, discord_id, party_name, timestamp):
        self.discord_id = discord_id
        self.party_name = party_name
        self.timestamp = timestamp
        
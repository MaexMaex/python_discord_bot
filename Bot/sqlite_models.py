class User:
        
    def __init__(self, discord_id, name, score, status):
        self.discord_id = discord_id
        self.name = name
        self.score = score
        self.status = status

class Bttn():

    def __init__(self, discord_id, party_name, timestamp):
        self.discord_id = discord_id
        self.party_name = party_name
        self.timestamp = timestamp
        
import random
from .data import COUNTRIES, COUNTRY_BY_KEY

def fmt(n: int) -> str:
    trans = str.maketrans("0123456789,-", "۰۱۲۳۴۵۶۷۸۹،−")
    return str(n).translate(trans)

class Game:
    def __init__(self, db):
        self.db = db
        self.seed_countries()

    def seed_countries(self):
        for c in COUNTRIES:
            self.db.execute(
                """INSERT OR IGNORE INTO countries
                (key,name,emoji,economy,industry,population,power,territory,treasury,research)
                VALUES(?,?,?,?,?,?,?,?,?,1)""",
                (c.key,c.name,c.emoji,c.economy,c.industry,c.population,c.power,c.territory,c.economy*10)
            )

    def turn(self):
        return self.db.fetchone("SELECT turn FROM game_state WHERE id=1")["turn"]

    def advance_turn(self):
        t = self.turn() + 1
        self.db.execute("UPDATE game_state SET turn=? WHERE id=1", (t,))
        return t

    def country(self, key):
        return self.db.fetchone("SELECT * FROM countries WHERE key=?", (key,))

    def register(self, guid, name):
        return self.db.execute(
            "INSERT OR IGNORE INTO players(guid,name) VALUES(?,?)", (guid, name)
        )

    def player(self, guid):
        return self.db.fetchone("SELECT * FROM players WHERE guid=?", (guid,))

    def choose(self, guid, key):
        if key not in COUNTRY_BY_KEY:
            raise ValueError("کشور پیدا نشد.")
        existing = self.db.fetchone("SELECT guid FROM players WHERE country_key=?", (key,))
        if existing and existing["guid"] != guid:
            raise ValueError("این کشور قبلاً انتخاب شده است.")
        self.db.execute("UPDATE players SET country_key=? WHERE guid=?", (key, guid))

    def income(self, guid):
        p = self.player(guid)
        if not p or not p["country_key"]:
            raise ValueError("ابتدا کشور انتخاب کن.")
        if p["last_income_turn"] >= self.turn():
            raise ValueError("در این نوبت درآمدت را قبلاً گرفته‌ای.")
        c = self.country(p["country_key"])
        amount = max(10, c["economy"] + c["industry"] // 2 + c["research"] * 5)
        self.db.execute("UPDATE countries SET treasury=treasury+? WHERE key=?", (amount, c["key"]))
        self.db.execute("UPDATE players SET last_income_turn=? WHERE guid=?", (self.turn(), guid))
        return amount

    def power(self, c):
        return c["power"] + c["industry"] // 2 + c["economy"] // 3 + c["research"] * 15 + c["territory"] * 2

    def attack(self, guid, target_key):
        p = self.player(guid)
        if not p or not p["country_key"]:
            raise ValueError("ابتدا کشور انتخاب کن.")
        attacker_key = p["country_key"]
        if attacker_key == target_key:
            raise ValueError("نمی‌توانی به کشور خودت حمله کنی.")
        a, d = self.country(attacker_key), self.country(target_key)
        if not d:
            raise ValueError("کشور هدف پیدا نشد.")
        cost = 40
        if a["treasury"] < cost:
            raise ValueError("خزانه برای شروع جنگ کافی نیست.")
        self.db.execute("UPDATE countries SET treasury=treasury-? WHERE key=?", (cost, attacker_key))
        ascore = self.power(a) + random.randint(-35, 35)
        dscore = self.power(d) + random.randint(-35, 35)
        winner = attacker_key if ascore >= dscore else target_key
        if winner == attacker_key:
            gain = max(1, d["territory"] // 5)
            self.db.execute("UPDATE countries SET territory=territory+?, treasury=treasury+? WHERE key=?", (gain, cost, attacker_key))
            self.db.execute("UPDATE countries SET territory=max(1,territory-?) WHERE key=?", (gain, target_key))
        self.db.execute(
            "INSERT INTO wars(attacker,defender,attacker_score,defender_score,winner,turn) VALUES(?,?,?,?,?,?)",
            (attacker_key,target_key,ascore,dscore,winner,self.turn())
        )
        return {"attacker":a, "defender":d, "ascore":ascore, "dscore":dscore, "winner":winner}

    def leaderboard(self, limit=10):
        return self.db.fetchall(
            "SELECT * FROM countries ORDER BY (power + industry/2 + economy/3 + research*15 + territory*2) DESC LIMIT ?",
            (limit,)
        )

    def alliances(self, key):
        return self.db.fetchall(
            "SELECT relation,b FROM relations WHERE a=? UNION ALL SELECT relation,a FROM relations WHERE b=?",
            (key,key)
        )

    def set_relation(self, a, b, relation):
        self.db.execute("INSERT OR REPLACE INTO relations(a,b,relation) VALUES(?,?,?)", (a,b,relation))
        self.db.execute("INSERT OR REPLACE INTO relations(a,b,relation) VALUES(?,?,?)", (b,a,relation))

    def admin_give(self, key, amount):
        if not self.country(key): raise ValueError("کشور پیدا نشد.")
        self.db.execute("UPDATE countries SET treasury=treasury+? WHERE key=?", (amount,key))

    def admin_setpower(self, key, amount):
        if not self.country(key): raise ValueError("کشور پیدا نشد.")
        self.db.execute("UPDATE countries SET power=max(1,?) WHERE key=?", (amount,key))

    def admin_reset(self, key):
        c = COUNTRY_BY_KEY.get(key)
        if not c: raise ValueError("کشور پیدا نشد.")
        self.db.execute("""UPDATE countries SET economy=?,industry=?,population=?,power=?,territory=?,treasury=?,research=1 WHERE key=?""",
                         (c.economy,c.industry,c.population,c.power,c.territory,c.economy*10,c.key))

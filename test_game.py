import tempfile
from app.db import Database
from app.game import Game

def test_register_choose_and_income():
    with tempfile.TemporaryDirectory() as d:
        db = Database(d + "/x.db")
        game = Game(db)
        game.register("u1", "Test")
        game.choose("u1", "ireland")
        amount = game.income("u1")
        assert amount > 0
        assert game.player("u1")["country_key"] == "ireland"

def test_attack_changes_game_state():
    with tempfile.TemporaryDirectory() as d:
        db = Database(d + "/x.db")
        game = Game(db)
        game.register("u1", "A")
        game.choose("u1", "ireland")
        result = game.attack("u1", "france")
        assert result["winner"] in ("ireland", "france")
        assert db.fetchone("SELECT COUNT(*) c FROM wars")["c"] == 1

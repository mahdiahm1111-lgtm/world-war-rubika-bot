import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    rubika_token: str
    owner_guid: str
    db_path: str = "data/game.db"

def load_settings() -> Settings:
    token = os.getenv("RUBIKA_TOKEN", "").strip()
    owner = os.getenv("OWNER_GUID", "").strip()
    db = os.getenv("DB_PATH", "data/game.db").strip() or "data/game.db"
    if not token or token.startswith("PASTE_"):
        raise RuntimeError("RUBIKA_TOKEN is missing in .env")
    if not owner or owner.startswith("PASTE_"):
        raise RuntimeError("OWNER_GUID is missing in .env")
    return Settings(token, owner, db)

from pathlib import Path

import rtoml

from scraper.models import Listing

STATE_FILE = Path("seen.toml")


def load_seen() -> dict[str, list[str]]:
    if not STATE_FILE.exists():
        return {}
    return rtoml.load(STATE_FILE)


def save_seen(seen: dict[str, list[str]]) -> None:
    rtoml.dump(seen, STATE_FILE)


def filter_new(scraper_name: str, listings: list[Listing], seen: dict[str, list[str]]) -> list[Listing]:
    seen_ids = set(seen.get(scraper_name, []))
    return [l for l in listings if l.id not in seen_ids]

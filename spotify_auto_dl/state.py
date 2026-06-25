import json
from datetime import datetime, timezone
from pathlib import Path


STATE_FILE = Path("~/.spotify-auto-dl/state.json").expanduser()


class State:
    def __init__(self, path: Path = STATE_FILE):
        self._path = path
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict[str, dict]:
        if not self._path.exists():
            return {}
        with open(self._path) as f:
            return json.load(f)

    def is_downloaded(self, track_id: str, title: str | None = None) -> bool:
        if track_id in self._data:
            return True
        if title is not None:
            normalized = title.lower().strip()
            return any(v["title"].lower().strip() == normalized for v in self._data.values())
        return False

    def mark_downloaded(self, track_id: str, title: str, artist: str, album: str) -> None:
        self._data[track_id] = {
            "title": title,
            "artist": artist,
            "album": album,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
        }

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)

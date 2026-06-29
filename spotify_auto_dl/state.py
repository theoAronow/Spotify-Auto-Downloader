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

    def _entry_matches(self, entry: dict, title: str) -> bool:
        return entry.get("title", "").lower().strip() == title.lower().strip()

    def is_downloaded(self, track_id: str, title: str | None = None) -> bool:
        entry = self._data.get(track_id)
        if entry and entry.get("status", "downloaded") == "downloaded":
            return True
        if title is not None:
            return any(
                self._entry_matches(v, title) and v.get("status", "downloaded") == "downloaded"
                for v in self._data.values()
            )
        return False

    def is_skipped(self, track_id: str, title: str | None = None) -> bool:
        entry = self._data.get(track_id)
        if entry and entry.get("status") in ("skipped", "failed"):
            return True
        if title is not None:
            return any(
                self._entry_matches(v, title) and v.get("status") in ("skipped", "failed")
                for v in self._data.values()
            )
        return False

    def mark_downloaded(self, track_id: str, title: str, artist: str, album: str) -> None:
        self._data[track_id] = {
            "status": "downloaded",
            "title": title,
            "artist": artist,
            "album": album,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
        }

    def mark_skipped(self, track_id: str, title: str, artist: str, album: str) -> None:
        self._data[track_id] = {
            "status": "skipped",
            "title": title,
            "artist": artist,
            "album": album,
            "skipped_at": datetime.now(timezone.utc).isoformat(),
        }

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)

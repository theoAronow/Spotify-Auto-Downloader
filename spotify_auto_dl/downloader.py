import os
from spotdl import Spotdl
from spotdl.types.song import Song

from .config import Config
from .state import State


def _init_client(config: Config) -> Spotdl:
    return Spotdl(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        downloader_settings={
            "output": str(config.download_dir / config.output.format),
            "format": config.output.audio_format,
            "bitrate": config.output.bitrate,
        },
    )


def _new_songs(client: Spotdl, artist_url: str, state: State) -> list[Song]:
    all_songs: list[Song] = client.search([artist_url])
    return [s for s in all_songs if not state.is_downloaded(s.song_id)]


def sync(config: Config, state: State) -> None:
    client = _init_client(config)

    for artist in config.artists:
        print(f"Checking {artist.name}...")
        new_songs = _new_songs(client, str(artist.url), state)

        if not new_songs:
            print(f"  No new tracks.")
            continue

        print(f"  {len(new_songs)} new track(s) found.")
        for song in new_songs:
            _, path = client.download(song)
            if path:
                state.mark_downloaded(
                    track_id=song.song_id,
                    title=song.name,
                    artist=song.artist,
                    album=song.album_name,
                )
                print(f"  Downloaded: {song.name}")
            else:
                print(f"  Failed: {song.name}")

    state.save()

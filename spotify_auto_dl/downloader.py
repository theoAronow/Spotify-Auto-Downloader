import os
from urllib.parse import urlparse

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotdl import Spotdl
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from .config import Config
from .state import State

console = Console()


def _init_spotify() -> spotipy.Spotify:
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
    ))


def _init_spotdl(config: Config) -> Spotdl:
    return Spotdl(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        downloader_settings={
            "output": str(config.download_dir / config.output.format),
            "format": config.output.audio_format,
            "bitrate": config.output.bitrate,
        },
    )


def _get_discography(sp: spotipy.Spotify, artist_id: str) -> list[dict]:
    albums = []
    results = sp.artist_albums(artist_id, album_type="album,single,compilation", limit=50)
    albums.extend(results["items"])
    while results["next"]:
        results = sp.next(results)
        albums.extend(results["items"])

    all_tracks = []
    seen_names: set[str] = set()
    for album in albums:
        track_results = sp.album_tracks(album["id"], limit=50)
        tracks = track_results["items"]
        while track_results["next"]:
            track_results = sp.next(track_results)
            tracks.extend(track_results["items"])

        for track in tracks:
            artist_ids_on_track = [a["id"] for a in track["artists"]]
            if artist_id in artist_ids_on_track:
                name_lower = track["name"].lower()
                if name_lower not in seen_names:
                    seen_names.add(name_lower)
                    all_tracks.append({
                        "id": track["id"],
                        "name": track["name"],
                        "album": album["name"],
                    })
    return all_tracks


def sync(config: Config, state: State) -> None:
    sp = _init_spotify()
    spotdl_client = _init_spotdl(config)

    for artist in config.artists:
        console.rule(f"[bold]{artist.name}")
        artist_id = urlparse(str(artist.url)).path.split("/")[-1]

        with console.status("[bold]Fetching discography...[/]", spinner="dots"):
            all_tracks = _get_discography(sp, artist_id)

        console.print(f"  Found [bold]{len(all_tracks)}[/] total tracks:\n")

        new_tracks = []
        for track in all_tracks:
            already = state.is_downloaded(track["id"])
            status = "[dim]already downloaded[/dim]" if already else "[green]new[/green]"
            console.print(f"    {track['name']} — [dim]{track['album']}[/dim] [{status}]")
            if not already:
                new_tracks.append(track)

        if not new_tracks:
            console.print("\n  [green]Already up to date.[/]")
            continue

        console.print(f"\n  [bold]{len(new_tracks)} new track(s) to download.[/]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading...", total=len(new_tracks))

            for track in new_tracks:
                progress.update(task, description=f"[cyan]{track['name']}[/]")
                track_url = f"https://open.spotify.com/track/{track['id']}"
                songs = spotdl_client.search([track_url])
                if songs:
                    _, path = spotdl_client.download(songs[0])
                    if path:
                        state.mark_downloaded(
                            track_id=track["id"],
                            title=track["name"],
                            artist=artist.name,
                            album=track["album"],
                        )
                    else:
                        console.print(f"  [red]Failed:[/] {track['name']}")
                else:
                    console.print(f"  [red]Not found on YouTube:[/] {track['name']}")
                progress.advance(task)

    state.save()
    console.print("\n[bold green]Sync complete.[/]")

import time
import os
import click
import yaml
import spotipy
from dotenv import load_dotenv
from pathlib import Path
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse

load_dotenv()

from .config import load_config
from .downloader import sync as run_sync
from .state import State


@click.group()
def cli():
    """Automatically download new releases from your favorite Spotify artists."""


@cli.command()
@click.option(
    "--config",
    "config_path",
    default="config.yaml",
    type=click.Path(exists=True, path_type=Path),
    help="Path to your config.yaml file.",
)
@click.option(
    "--daemon",
    is_flag=True,
    default=False,
    help="Run on a loop using the interval defined in config.",
)
def sync(config_path: Path, daemon: bool) -> None:
    """Sync new tracks for all artists in your config."""
    config = load_config(config_path)
    state = State()

    if not daemon:
        run_sync(config, state)
        return

    if config.schedule.run_on_start:
        run_sync(config, state)

    interval_seconds = config.schedule.interval_hours * 3600
    click.echo(f"Daemon started. Syncing every {config.schedule.interval_hours}h.")
    while True:
        time.sleep(interval_seconds)
        run_sync(config, state)


@cli.command("init")
@click.option(
    "--config",
    "config_path",
    default="config.yaml",
    type=click.Path(path_type=Path),
    help="Where to create the config file.",
)
def init(config_path: Path) -> None:
    """Create a starter config.yaml in the current directory."""
    if config_path.exists():
        click.confirm(f"{config_path} already exists. Overwrite?", abort=True)

    default_config = {
        "download_dir": str(Path("~/Music/spotify-auto-dl").expanduser()),
        "artists": [],
        "schedule": {
            "interval_hours": 24,
            "run_on_start": True,
        },
        "output": {
            "format": "{artist}/{album}/{title}.{output-ext}",
            "audio_format": "mp3",
            "bitrate": "320k",
        },
    }

    with open(config_path, "w") as f:
        yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

    click.echo(f"Created {config_path}.")
    click.echo("Next steps:")
    click.echo("  1. Set your download directory:  spotify-auto-dl set-destination /path/to/music")
    click.echo("  2. Add an artist:                spotify-auto-dl add-artist \"<spotify artist url>\"")
    click.echo("  3. Run a sync:                   spotify-auto-dl sync")


@cli.command("add-artist")
@click.argument("url")
@click.option(
    "--config",
    "config_path",
    default="config.yaml",
    type=click.Path(path_type=Path),
    help="Path to your config.yaml file.",
)
def add_artist(url: str, config_path: Path) -> None:
    """Add an artist to your config by Spotify URL."""
    artist_id = urlparse(url).path.split("/")[-1]

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
    ))
    artist_data = sp.artist(artist_id)
    name = artist_data["name"]

    with open(config_path) as f:
        config = yaml.safe_load(f)

    for existing in config.get("artists", []):
        if existing["url"] == url:
            click.echo(f"{name} is already in your config.")
            return

    config.setdefault("artists", []).append({"name": name, "url": url})

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    click.echo(f"Added {name} to {config_path}.")


@cli.command("set-destination")
@click.argument("path")
@click.option(
    "--config",
    "config_path",
    default="config.yaml",
    type=click.Path(path_type=Path),
    help="Path to your config.yaml file.",
)
def set_destination(path: str, config_path: Path) -> None:
    """Set the download directory in your config."""
    destination = Path(path).expanduser().resolve()

    if not destination.exists():
        click.confirm(f"{destination} does not exist. Create it?", abort=True)
        destination.mkdir(parents=True)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    config["download_dir"] = str(destination)

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    click.echo(f"Download directory set to {destination}.")

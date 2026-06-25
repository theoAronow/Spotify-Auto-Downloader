# Spotify Auto Downloader

Automatically download new releases from your favorite Spotify artists to a local drive. Tracks artists you care about, downloads only songs you don't already have, and can run on a schedule to stay up to date automatically.

## How It Works

1. You provide a list of Spotify artist URLs in a config file
2. On each run, the tool fetches each artist's full discography from Spotify
3. It compares against a local state file to find tracks you don't have yet
4. New tracks are downloaded as MP3s via [spotdl](https://github.com/spotDL/spotify-downloader)
5. The state file is updated so those tracks are skipped on future runs

---

## Requirements

- Python 3.10 or higher
- A [Spotify Developer account](https://developer.spotify.com/dashboard) (free)
- `ffmpeg` installed on your machine

Install ffmpeg on Mac:
```bash
brew install ffmpeg
```

---

## Installation

**1. Clone the repo**
```bash
git clone https://github.com/your-username/spotify-auto-downloader.git
cd spotify-auto-downloader
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install the package**
```bash
pip install .
```

---

## Spotify API Credentials

This tool uses the Spotify API to look up artist discographies. You need a free client ID and secret.

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Click **Create App**
3. Fill in any name and description, set the redirect URI to `http://localhost`
4. Open the app and copy the **Client ID** and **Client Secret**

**4. Set up your credentials**
```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

---

## Configuration

**5. Create your config file**
```bash
cp config.yaml.example config.yaml
```

Open `config.yaml` and edit it:
```yaml
download_dir: ~/Music/spotify-auto-dl

artists:
  - name: Daniel Caesar
    url: https://open.spotify.com/artist/20wkVLutqVOYrc0kxFs7rA

schedule:
  interval_hours: 24
  run_on_start: true

output:
  format: "{artist}/{album}/{title}.{output-ext}"
  audio_format: mp3
  bitrate: 320k
```

To get an artist URL: open Spotify → artist page → three dots → **Share** → **Copy Artist Link**.

---

## Usage

### Run a one-time sync
```bash
spotify-auto-dl sync
```

### Run continuously on a schedule
```bash
spotify-auto-dl sync --daemon
```
Syncs immediately on start (if `run_on_start: true`), then again every `interval_hours` hours.

### Add an artist
```bash
spotify-auto-dl add-artist "https://open.spotify.com/artist/ARTIST_ID"
```
Looks up the artist name from Spotify automatically and adds them to `config.yaml`.

### Change the download directory
```bash
spotify-auto-dl set-destination /Volumes/MyDrive/Music
```
Updates `download_dir` in `config.yaml`. Creates the directory if it doesn't exist.

### Use a custom config file path
```bash
spotify-auto-dl sync --config /path/to/my-config.yaml
```

---

## File Organization

Downloaded files are organized using the `output.format` template in `config.yaml`:

```
{download_dir}/
└── {artist}/
    └── {album}/
        └── {title}.mp3
```

For example:
```
~/Music/spotify-auto-dl/
└── Daniel Caesar/
    └── Freudian/
        ├── Get You (feat. Kali Uchis).mp3
        └── Best Part (feat. H.E.R.).mp3
```

---

## State File

Downloaded tracks are recorded in `~/.spotify-auto-dl/state.json`. This file is how the tool knows what you already have — it prevents re-downloading songs across runs. Do not delete it unless you want to re-download everything.

---

## Running on a Schedule (without --daemon)

If you'd rather use your system's scheduler instead of the built-in daemon:

**Mac/Linux (cron)**
```bash
crontab -e
```
Add a line to run every day at 6am:
```
0 6 * * * /path/to/.venv/bin/spotify-auto-dl sync --config /path/to/config.yaml
```

**Finding your full path:**
```bash
which spotify-auto-dl
```

---

## Troubleshooting

**`KeyError: SPOTIFY_CLIENT_ID`**
Your `.env` file is missing or the variable names are misspelled. Make sure `.env` exists in the directory where you run the command.

**`FileNotFoundError: config.yaml`**
Run the command from the project directory, or use `--config /full/path/to/config.yaml`.

**A track shows as new every run**
The same song can have different Spotify IDs across album versions, deluxe editions, and singles. The tool checks by both ID and title to handle this, but edge cases may occur.

**Downloads are slow**
Normal — each track requires finding a matching audio source on YouTube. The first run is the slowest since it downloads everything. Future runs only download new releases.

---

## License

MIT

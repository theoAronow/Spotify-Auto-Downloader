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

### Run continuously on a schedule (daemon mode)
```bash
spotify-auto-dl sync --daemon
```
Syncs immediately on start (if `run_on_start: true`), then again every `interval_hours` hours. See [Scheduling](#scheduling) for when to use this vs cron.

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

## Scheduling

There are two ways to run this tool automatically: **daemon mode** and **cron**. They accomplish the same goal differently.

### Daemon vs Cron

| | Daemon (`--daemon`) | Cron |
|---|---|---|
| How it works | Python process that sleeps and loops forever | OS wakes the command at a set time, it runs once and exits |
| Requires terminal open | Yes | No |
| Survives reboot | No | Yes |
| Easy to stop | `Ctrl+C` | `crontab -e` to remove |
| Best for | Servers, Docker containers | Personal computers |

**For a personal Mac, cron is recommended.** The daemon requires a terminal window to stay open and won't restart if you reboot. Cron is managed by the OS and runs reliably in the background.

---

### Setting Up Cron (Recommended for Mac)

**Step 1 — open your crontab**
```bash
crontab -e
```
This opens a text editor. If it opens vim, press `i` to start typing.

**Step 2 — add this line** (runs every day at 6am)
```
0 6 * * * cd /Users/theoaronow/Documents/Spotify-Auto-Downloader && SPOTIFY_CLIENT_ID=your_id SPOTIFY_CLIENT_SECRET=your_secret /Users/theoaronow/Documents/Spotify-Auto-Downloader/.venv/bin/spotify-auto-dl sync --config /Users/theoaronow/Documents/Spotify-Auto-Downloader/config.yaml >> /Users/theoaronow/.spotify-auto-dl/cron.log 2>&1
```

Replace `your_id` and `your_secret` with the values from your `.env` file. The credentials must be inline because cron does not load `.env` files automatically.

**Step 3 — save and exit**

If using vim: press `Esc`, type `:wq`, press `Enter`.

**Step 4 — verify it saved**
```bash
crontab -l
```

**Changing the schedule** — edit the `0 6 * * *` part:
```
0 8 * * *     every day at 8am
0 6 * * 1     every Monday at 6am
0 6,18 * * *  every day at 6am and 6pm
```

**Checking the log after it runs:**
```bash
cat ~/.spotify-auto-dl/cron.log
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

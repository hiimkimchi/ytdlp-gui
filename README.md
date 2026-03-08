# YTDLP Gui

A minimal macOS GUI wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp).

---

## Features

- Download video or audio-only from any yt-dlp–supported site
- Quality selector: Best / 1080p / 720p / 480p / 360p / Worst
- Format selector: mp4, mkv, webm, mov — or mp3, m4a, flac, wav for audio
- Live progress bar with speed & ETA
- Scrollable log pane
- Preferences saved between sessions

---

## Installation

**Homebrew (recommended)** — it manages Python, tkinter, yt-dlp, and ffmpeg for you.

```bash
brew install hiimkimchi/ytdlpgui/ytdlpgui
```

To add the app to **/Applications** (so it appears in Finder and Spotlight), run once after install:

```bash
ln -sf "/opt/homebrew/opt/ytdlpgui/Applications/ytdlp gui.app" "/Applications/ytdlp gui.app"
```

Then launch from the terminal or by opening the app from Finder/Spotlight:

```bash
ytdlpgui
```

Homebrew installs **yt-dlp** and **ffmpeg** as dependencies if they aren't already present.

---

## Install via pip

```bash
pip install git+https://github.com/hiimkimchi/ytdlp-gui.git
ytdlpgui
```

> **Note:** You still need `yt-dlp` and `ffmpeg` on your PATH:
> ```bash
> brew install yt-dlp ffmpeg
> ```

---

## Build a standalone .app bundle

You need a Python with tkinter to build (so the app can open). If you use Homebrew Python, install it first:

```bash
brew install python-tk@3.12
```

Then build the app:

```bash
git clone https://github.com/hiimkimchi/ytdlp-gui.git
cd ytdlp-gui
chmod +x extras/build_app.sh
./extras/build_app.sh
```

Install and launch:

```bash
# Copy to Applications (then launch from Finder or Spotlight)
cp -r "dist/ytdlp gui.app" /Applications/

# Or run once from the project:
open "dist/ytdlp gui.app"
```

The .app bundles its own Python and dependencies; **yt-dlp** and **ffmpeg** must still be installed on the Mac (e.g. `brew install yt-dlp ffmpeg`).

---

## Requirements

| Dependency | Version  | Notes                        |
|------------|----------|------------------------------|
| Python     | ≥ 3.10   | tkinter included on macOS    |
| yt-dlp     | latest   | `brew install yt-dlp`        |
| ffmpeg     | any      | needed for merging & audio   |

---
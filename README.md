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

## Install via Homebrew (recommended)

First, tap the custom formula:

```bash
brew tap hiimkimchi/ytdlpgui https://github.com/hiimkimchi/ytdlp-gui
brew install ytdlpgui
```

Then launch:

```bash
ytdlpgui
```

This will also install **yt-dlp** and **ffmpeg** as dependencies if they aren't already present.

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

```bash
git clone https://github.com/YOUR_USERNAME/ytdlp-wrapper.git
cd ytdlp-wrapper
chmod +x extras/build_app.sh
./extras/build_app.sh

# Then drag to /Applications:
cp -r "dist/ytdlp gui.app" /Applications/
```

---

## Requirements

| Dependency | Version  | Notes                        |
|------------|----------|------------------------------|
| Python     | ≥ 3.10   | tkinter included on macOS    |
| yt-dlp     | latest   | `brew install yt-dlp`        |
| ffmpeg     | any      | needed for merging & audio   |

---
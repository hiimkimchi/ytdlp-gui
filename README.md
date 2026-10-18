# YTDLP Gui

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![Homebrew](https://img.shields.io/badge/homebrew-tap-orange?logo=homebrew)](https://github.com/hiimkimchi/homebrew-ytdlpgui)

A minimal macOS GUI wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp).

---

## Features

- **YouTube Download** — best-quality audio as mp3 from any yt-dlp–supported site
- **Stem Splitter** — split a song into Vocals, Drums, Instruments, and Bass with [demucs](https://github.com/adefossez/demucs)
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

Homebrew installs **ffmpeg**, plus **yt-dlp** (with the deno JS runtime) and **demucs** (with PyTorch, ~650 MB) inside the app.

The first stem split downloads the demucs model (~80 MB). Stems are saved as mp3 to `<Save To>/htdemucs/<song name>/`.

---

## Install via pip

```bash
pip install git+https://github.com/hiimkimchi/ytdlp-gui.git
ytdlpgui
```

> **Note:** yt-dlp and demucs are installed with it, but you still need `ffmpeg`:
> ```bash
> brew install ffmpeg
> ```

---

## Requirements

| Dependency | Version  |
|------------|----------|
| Python     | ≥ 3.10   |
| yt-dlp     | latest   |
| ffmpeg     | any      |
| demucs     | ≥ 4.1    |

---

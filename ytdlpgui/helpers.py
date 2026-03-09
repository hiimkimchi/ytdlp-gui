from urllib.parse import urlparse, parse_qs, urlunparse
import os
import subprocess

def normalize_single_video_url(url: str) -> str:
    """Strip playlist/mix params from YouTube URLs so only the single video is downloaded."""
    url = url.strip()
    parsed = urlparse(url)

    # youtube.com/watch?v=VIDEO_ID&list=... → keep only v=VIDEO_ID
    if "youtube.com" in parsed.netloc and parsed.path in ("/watch", "/watch/"):
        qs = parse_qs(parsed.query)
        if "v" in qs:
            vid = qs["v"][0]
            return f"https://www.youtube.com/watch?v={vid}"

    # youtu.be/VIDEO_ID?list=...
    if parsed.netloc == "youtu.be" and parsed.path:
        vid = parsed.path.lstrip("/").split("?")[0]
        if vid:
            return f"https://www.youtube.com/watch?v={vid}"
    return url


def find_ytdlp() -> str | None:
    """Return path to yt-dlp binary or None."""
    for candidate in ("yt-dlp", "/opt/homebrew/bin/yt-dlp", "/usr/local/bin/yt-dlp"):
        try:
            subprocess.run([candidate, "--version"], capture_output=True, check=True)
            return candidate
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    return None


def find_ffmpeg_dir() -> str | None:
    """Return directory containing ffmpeg and ffprobe, or None.
    Checks Homebrew paths first so GUI launches (no shell PATH) still find ffmpeg.
    """
    for dir_candidate in ("/opt/homebrew/bin", "/usr/local/bin"):
        ffmpeg = os.path.join(dir_candidate, "ffmpeg")
        ffprobe = os.path.join(dir_candidate, "ffprobe")
        if os.path.isfile(ffmpeg) and os.path.isfile(ffprobe):
            try:
                subprocess.run([ffmpeg, "-version"], capture_output=True, check=True)
                return dir_candidate
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
    return None

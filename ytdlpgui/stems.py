import importlib.util
import os
import re
import sys
from pathlib import Path

from .downloader import DownloadRunner

MODEL = "htdemucs"

# UI label -> demucs source name
STEMS = {
    "Vocals":      "vocals",
    "Drums":       "drums",
    "Instruments": "other",
    "Bass":        "bass",
}

AUDIO_FILETYPES = [
    ("Audio files", "*.mp3 *.wav *.flac *.m4a *.aac *.ogg *.opus *.aiff *.aif"),
    ("All files", "*"),
]

TQDM_RE = re.compile(r'^\s*(\d+)%\|.*?\[(\S+)<(\S+?),')


def find_demucs() -> list[str] | None:
    """Return the command prefix used to invoke demucs, or None."""
    if importlib.util.find_spec("demucs") is not None:
        return [sys.executable, "-m", "demucs.separate"]
    for candidate in (
        Path.home() / ".local/bin/demucs",
        Path("/opt/homebrew/bin/demucs"),
        Path("/usr/local/bin/demucs"),
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return [str(candidate)]
    return None


def stems_dir(out_dir: str, track_path: str) -> Path:
    """Folder demucs writes the stems of `track_path` into."""
    return Path(out_dir) / MODEL / Path(track_path).name.rsplit(".", 1)[0]


def build_stem_cmd(demucs: list[str], track_path: str, out_dir: str,
                   stems: list[str]) -> list[str]:
    """Build the demucs command. `stems` are demucs source names."""
    cmd = demucs + ["-n", MODEL, "--mp3", "-o", out_dir]
    if len(stems) == 1:
        cmd += ["--two-stems", stems[0], "--other-method", "none"]
    cmd.append(track_path)
    return cmd


def prune_stems(out_dir: str, track_path: str, keep: list[str]) -> None:
    """Delete stems demucs produced that the user didn't ask for."""
    folder = stems_dir(out_dir, track_path)
    for name in STEMS.values():
        if name not in keep:
            (folder / f"{name}.mp3").unlink(missing_ok=True)


class StemRunner(DownloadRunner):
    """Runs demucs in a background thread, reporting tqdm progress."""

    def _is_noise(self, line: str) -> bool:
        return bool(TQDM_RE.search(line))

    def _parse_line(self, line: str):
        m = TQDM_RE.search(line)
        if m and self.on_progress:
            self.on_progress(int(m.group(1)) / 100, m.group(2), m.group(3))
        elif line.startswith("Separating track") and self.on_status:
            self.on_status("splitting")

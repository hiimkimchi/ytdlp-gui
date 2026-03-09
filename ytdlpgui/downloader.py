import os
import re
import subprocess
import threading
from .helpers import normalize_single_video_url
from .const import QUALITY_MAP

PROGRESS_RE = re.compile(
    r'\[download\]\s+([\d.]+)%.*?at\s+([\d.]+\w+/s).*?ETA\s+(\S+)'
)


def build_cmd(ytdlp: str, mode: str, quality: str, fmt: str,
              out_dir: str, url: str, *, ffmpeg_dir: str | None = None) -> list[str]:
    """Build the yt-dlp command list from the current settings."""
    url = normalize_single_video_url(url)
    cmd = [ytdlp, "--newline"]

    if ffmpeg_dir:
        cmd += ["--ffmpeg-location", ffmpeg_dir]

    if mode == "audio":
        cmd += ["-x", "--audio-format", fmt, "--audio-quality", "0"]
    else:
        cmd += ["-f", QUALITY_MAP.get(quality, "best"),
                "--merge-output-format", fmt]

    cmd += ["-o", os.path.join(out_dir, "%(title)s.%(ext)s"), url]
    return cmd


class DownloadRunner:
    """
    runs a yt-dlp download in a background thread.
    """

    def __init__(self, cmd: list[str], *,
                 on_line: callable = None,
                 on_progress: callable = None,
                 on_status: callable = None,
                 on_done: callable = None):
        self.cmd = cmd
        self.on_line = on_line
        self.on_progress = on_progress
        self.on_status = on_status
        self.on_done = on_done
        self.proc: subprocess.Popen | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self.proc:
            self.proc.terminate()

    def _run(self):
        try:
            self.proc = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            for line in self.proc.stdout:
                line = line.rstrip()
                if self.on_line:
                    self.on_line(line)
                self._parse_line(line)

            self.proc.wait()
            rc = self.proc.returncode
            if self.on_done:
                self.on_done(rc)
        except Exception as exc:
            if self.on_done:
                self.on_done(None, exc)
        finally:
            self.proc = None

    def _parse_line(self, line: str):
        m = PROGRESS_RE.search(line)
        if m:
            pct = float(m.group(1)) / 100
            speed = m.group(2)
            eta = m.group(3)
            if self.on_progress:
                self.on_progress(pct, speed, eta)
            return

        if "[Merger]" in line or "[ffmpeg]" in line:
            if self.on_status:
                self.on_status("processing")
        elif "[download] Destination:" in line:
            if self.on_status:
                self.on_status("downloading")

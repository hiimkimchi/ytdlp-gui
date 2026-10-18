import importlib.util
import sys
from pathlib import Path

PACKAGES = ["yt-dlp[default,deno]", "demucs", "numpy"]


def build_update_cmd() -> list[str] | None:
    """pip command that upgrades yt-dlp and demucs in this app's environment.
    Returns None outside a virtualenv so we never touch a shared Python.
    """
    if sys.prefix == sys.base_prefix:
        return None
    args = ["--disable-pip-version-check", "install", "--upgrade", *PACKAGES]
    if importlib.util.find_spec("pip") is not None:
        return [sys.executable, "-m", "pip", *args]
    base = Path(sys.base_prefix) / "bin" / f"python{sys.version_info.major}.{sys.version_info.minor}"
    return [str(base), "-m", "pip", f"--python={sys.executable}", *args]

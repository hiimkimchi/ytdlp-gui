"""
ytdlpgui — a minimal macOS GUI wrapper around yt-dlp
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from .const import THEMES
from .helpers import find_ffmpeg_dir, find_ytdlp
from .widgets import ThemeMixin
from .downloader import build_cmd, DownloadRunner
from .prefs import load_prefs, save_prefs
from .stems import (AUDIO_FILETYPES, STEMS, StemRunner, build_stem_cmd,
                    find_demucs, prune_stems, stems_dir)


class App(ThemeMixin, tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ytdlp gui")
        self.resizable(False, False)

        # Prefs
        self.prefs_path = Path.home() / ".ytdlpgui_prefs.json"
        self.prefs = load_prefs(self.prefs_path)

        # Theme
        self.theme = self.prefs.get("theme", "dark")
        if self.theme not in THEMES:
            self.theme = "dark"
        self.colors = THEMES[self.theme].copy()
        self._init_theme()

        self.configure(bg=self.colors["BG"])

        # State
        self.ytdlp = find_ytdlp()
        self.running = False
        self._runner: DownloadRunner | None = None

        self._build_ui()
        self._center()

        if not self.ytdlp:
            self.after(300, self._warn_missing)

    # UI layout
    def _build_ui(self):
        PAD = 24
        c = self.colors

        # head
        header = tk.Frame(self, bg=c["BG"])
        header.pack(fill="x", padx=PAD, pady=(PAD, 0))
        self._theme_widgets.append((header, {"bg": "BG"}))

        title_accent = tk.Label(header, text="yt", font=("Helvetica Neue", 28, "bold"),
                                fg=c["ACCENT"], bg=c["BG"])
        title_accent.pack(side="left")
        self._theme_widgets.append((title_accent, {"fg": "ACCENT", "bg": "BG"}))

        title_text = tk.Label(header, text="dlp", font=("Helvetica Neue", 28, "bold"),
                              fg=c["TEXT"], bg=c["BG"])
        title_text.pack(side="left")
        self._theme_widgets.append((title_text, {"fg": "TEXT", "bg": "BG"}))

        title_dim = tk.Label(header, text=" gui", font=("Helvetica Neue", 28),
                             fg=c["TEXT_DIM"], bg=c["BG"])
        title_dim.pack(side="left")
        self._theme_widgets.append((title_dim, {"fg": "TEXT_DIM", "bg": "BG"}))

        version_label = tk.Label(header, text='yt-dlp v' + self._ytdlp_version(),
                                 font=("Menlo", 10), fg=c["MUTED"], bg=c["BG"])
        version_label.pack(side="right", pady=8)
        self._theme_widgets.append((version_label, {"fg": "MUTED", "bg": "BG"}))

        self._theme_btn = tk.Label(header, text="☀" if self.theme == "dark" else "☽",
                                   font=("Helvetica Neue", 14),
                                   bg=c["BTN"], fg=c["TEXT_DIM"], padx=8, pady=4, cursor="hand2")
        self._theme_btn.bind("<Button-1>", lambda e: self._toggle_theme())
        self._theme_btn.pack(side="right", padx=(0, 12))
        self._theme_widgets.append((self._theme_btn, {"bg": "BTN", "fg": "TEXT_DIM"}))

        # seperator
        divider = tk.Frame(self, bg=c["BORDER"], height=1)
        divider.pack(fill="x", padx=PAD, pady=(12, 20))
        self._theme_widgets.append((divider, {"bg": "BORDER"}))

        # body
        body = tk.Frame(self, bg=c["BG"])
        body.pack(fill="both", padx=PAD)
        self._theme_widgets.append((self, {"bg": "BG"}))
        self._theme_widgets.append((body, {"bg": "BG"}))

        # tabs
        tab_row = tk.Frame(body, bg=c["BG"])
        tab_row.pack(fill="x", pady=(0, 20))
        self._theme_widgets.append((tab_row, {"bg": "BG"}))

        self.tab_var = tk.StringVar(value=self.prefs.get("tab", "youtube"))
        if self.tab_var.get() not in ("youtube", "stems"):
            self.tab_var.set("youtube")
        self._toggle_btn(tab_row, "YouTube Download", "youtube", self.tab_var, self._on_tab)
        self._toggle_btn(tab_row, "Stem Splitter", "stems", self.tab_var, self._on_tab)

        tab_host = tk.Frame(body, bg=c["BG"])
        tab_host.pack(fill="x")
        self._theme_widgets.append((tab_host, {"bg": "BG"}))

        # youtube view
        self.yt_view = tk.Frame(tab_host, bg=c["BG"])
        self._theme_widgets.append((self.yt_view, {"bg": "BG"}))

        self._label(self.yt_view, "URL")
        url_row = tk.Frame(self.yt_view, bg=c["BG"])
        url_row.pack(fill="x", pady=(4, 16))
        self._theme_widgets.append((url_row, {"bg": "BG"}))

        self.url_var = tk.StringVar(value=self.prefs.get("last_url", ""))
        self.url_entry = self._entry(url_row, self.url_var,
                                     placeholder="https://youtube.com/watch?v=…")
        self.url_entry.pack(side="left", fill="x", expand=True)

        paste_btn = self._btn(url_row, "Paste", self._paste_url, style="ghost")
        paste_btn.pack(side="left", padx=(8, 0))

        # stem splitter view
        self.stem_view = tk.Frame(tab_host, bg=c["BG"])
        self._theme_widgets.append((self.stem_view, {"bg": "BG"}))

        self._label(self.stem_view, "FILE")
        file_row = tk.Frame(self.stem_view, bg=c["BG"])
        file_row.pack(fill="x", pady=(4, 16))
        self._theme_widgets.append((file_row, {"bg": "BG"}))

        self.stem_file_var = tk.StringVar(value="")
        self.stem_file_label = tk.Label(
            file_row, text="Click to choose an audio file…", anchor="w",
            font=("Helvetica Neue", 13), bg=c["SURFACE"], fg=c["MUTED"],
            padx=6, pady=4, cursor="hand2", highlightthickness=1,
            highlightbackground=c["BORDER"],
        )
        self.stem_file_label.pack(side="left", fill="x", expand=True)
        self.stem_file_label.bind("<Button-1>", lambda e: self._choose_stem_file())
        self._theme_widgets.append((self.stem_file_label,
                                    {"bg": "SURFACE", "highlightbackground": "BORDER"}))
        self.stem_file_label._refresh = lambda: self.stem_file_label.config(
            fg=self.colors["TEXT" if self.stem_file_var.get() else "MUTED"])
        self._theme_toggle_btns.append(self.stem_file_label)

        choose_btn = self._btn(file_row, "Choose…", self._choose_stem_file, style="ghost")
        choose_btn.pack(side="left", padx=(8, 0))

        self._label(self.stem_view, "STEMS")
        stems_row = tk.Frame(self.stem_view, bg=c["BG"])
        stems_row.pack(fill="x", pady=(4, 16))
        self._theme_widgets.append((stems_row, {"bg": "BG"}))

        saved_stems = self.prefs.get("stems", list(STEMS))
        self.stem_vars = {}
        for label in STEMS:
            self.stem_vars[label] = tk.BooleanVar(value=label in saved_stems)
            self._check_btn(stems_row, label, self.stem_vars[label])

        # output folder entry and browse button
        self._label(body, "SAVE TO")
        out_row = tk.Frame(body, bg=c["BG"])
        out_row.pack(fill="x", pady=(4, 20))
        self._theme_widgets.append((out_row, {"bg": "BG"}))

        self.out_var = tk.StringVar(value=self.prefs.get("out_dir", str(Path.home() / "Downloads")))
        self.out_entry = self._entry(out_row, self.out_var)
        self.out_entry.pack(side="left", fill="x", expand=True)

        browse_btn = self._btn(out_row, "Browse", self._browse, style="ghost")
        browse_btn.pack(side="left", padx=(8, 0))

        # progress bar and status label
        self.progress_frame = tk.Frame(body, bg=c["BG"])
        self.progress_frame.pack(fill="x", pady=(0, 16))
        self._theme_widgets.append((self.progress_frame, {"bg": "BG"}))

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(self.progress_frame, textvariable=self.status_var,
                                     font=("Menlo", 10), fg=c["TEXT_DIM"], bg=c["BG"], anchor="w")
        self.status_label.pack(fill="x")
        self._theme_widgets.append((self.status_label, {"fg": "TEXT_DIM", "bg": "BG"}))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = tk.Canvas(self.progress_frame, height=4, bg=c["SURFACE"],
                                      highlightthickness=0)
        self.progress_bar.pack(fill="x", pady=(4, 0))
        self.progress_bar.bind("<Configure>", lambda e: self._redraw_bar())
        self._bar_fill = self.progress_bar.create_rectangle(0, 0, 0, 4, fill=c["ACCENT"], width=0)
        self._theme_widgets.append((self.progress_bar, self._bar_fill, {"fill": "ACCENT"}))
        self._theme_widgets.append((self.progress_bar, {"bg": "SURFACE"}))

        self.meta_var = tk.StringVar(value="")
        self.meta_label = tk.Label(self.progress_frame, textvariable=self.meta_var,
                                   font=("Menlo", 9), fg=c["MUTED"], bg=c["BG"], anchor="w")
        self.meta_label.pack(fill="x", pady=(2, 0))
        self._theme_widgets.append((self.meta_label, {"fg": "MUTED", "bg": "BG"}))

        # log text widget
        self._label(body, "LOG")
        log_frame = tk.Frame(body, bg=c["SURFACE"], bd=0, highlightthickness=1,
                             highlightbackground=c["BORDER"])
        log_frame.pack(fill="x", pady=(4, 20))
        self._theme_widgets.append((log_frame, {"bg": "SURFACE", "highlightbackground": "BORDER"}))

        self.log = tk.Text(log_frame, height=6, bg=c["SURFACE"], fg=c["TEXT_DIM"],
                           font=("Menlo", 9), bd=0, padx=10, pady=8,
                           insertbackground=c["ACCENT"], state="disabled",
                           wrap="word", relief="flat")
        self.log.pack(fill="both", expand=True)
        self._theme_widgets.append((self.log, {"bg": "SURFACE", "fg": "TEXT_DIM",
                                               "insertbackground": "ACCENT"}))

        sb = ttk.Scrollbar(log_frame, command=self.log.yview)
        self.log["yscrollcommand"] = sb.set

        # action buttons
        btn_row = tk.Frame(body, bg=c["BG"])
        btn_row.pack(fill="x", pady=(0, PAD))
        self._theme_widgets.append((btn_row, {"bg": "BG"}))

        self.dl_btn = self._btn(btn_row, "Download", self._start, style="primary")
        self.dl_btn.pack(side="left", fill="x", expand=True)

        self.stop_btn = self._btn(btn_row, "Stop", self._stop_download, style="danger")
        self.stop_btn.pack(side="left", padx=(8, 0))
        self.stop_btn._disabled = True
        self.stop_btn.config(fg=self.colors["MUTED"])

        clear_btn = self._btn(btn_row, "Clear log", self._clear_log, style="ghost")
        clear_btn.pack(side="left", padx=(8, 0))

        self._on_tab()

    # app actions
    def _on_tab(self):
        for btn in self._toggle_btns:
            btn._refresh()
        stems = self.tab_var.get() == "stems"
        self.yt_view.pack_forget()
        self.stem_view.pack_forget()
        (self.stem_view if stems else self.yt_view).pack(fill="x")
        self.dl_btn.config(text="Split stems" if stems else "Download")
        if self.winfo_ismapped():
            self.update_idletasks()
            self.geometry(f"{self.winfo_width()}x{self.winfo_reqheight()}")

    def _choose_stem_file(self):
        current = self.stem_file_var.get()
        path = filedialog.askopenfilename(
            title="Choose a song to split",
            initialdir=str(Path(current).parent) if current else self.out_var.get(),
            filetypes=AUDIO_FILETYPES,
        )
        if path:
            self.stem_file_var.set(path)
            self.stem_file_label.config(text=Path(path).name)
            self.stem_file_label._refresh()

    def _start(self):
        if self.tab_var.get() == "stems":
            self._start_split()
        else:
            self._start_download()

    def _begin_run(self, status):
        self._save_prefs()
        self.running = True
        self.dl_btn._disabled = True
        self.dl_btn.config(fg=self.colors["MUTED"])
        self.stop_btn._disabled = False
        self.stop_btn.config(fg=self.colors["RED"])
        self._set_progress(0)
        self._set_status(status, self.colors["TEXT_DIM"])
        self.meta_var.set("")
        self._log_clear()

    def _start_split(self):
        demucs = find_demucs()
        if not demucs:
            self._warn_missing_demucs()
            return

        track = self.stem_file_var.get()
        if not track or not Path(track).is_file():
            messagebox.showwarning("No file", "Please choose an audio file to split.")
            return

        keep = [STEMS[label] for label, var in self.stem_vars.items() if var.get()]
        if not keep:
            messagebox.showwarning("No stems", "Please select at least one stem.")
            return

        out_dir = self.out_var.get()
        self._begin_run("Loading model…")

        env = os.environ.copy()
        ffmpeg_dir = find_ffmpeg_dir()
        if ffmpeg_dir:
            env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")

        cmd = build_stem_cmd(demucs, track, out_dir, keep)
        self._log(f"$ {' '.join(cmd)}\n")

        def _done(rc, exc=None):
            if rc == 0 and exc is None:
                prune_stems(out_dir, track, keep)
                folder = stems_dir(out_dir, track)
                self.after(0, lambda: self._log(f"\nStems saved to {folder}\n"))
            self._on_done(rc, exc)

        self._runner = StemRunner(
            cmd,
            on_line=lambda line: self.after(0, lambda l=line: self._log(l + "\n")),
            on_progress=self._on_stem_progress,
            on_status=self._on_dl_status,
            on_done=_done,
            env=env,
        )
        self._runner.start()

    def _on_stem_progress(self, pct, elapsed, remaining):
        self.after(0, lambda: self._set_progress(pct))
        self.after(0, lambda: self._set_status(f"Splitting  {int(pct * 100)}%",
                                               self.colors["ACCENT"]))
        self.after(0, lambda: self.meta_var.set(f"{elapsed} elapsed  •  ETA {remaining}"))

    def _paste_url(self):
        try:
            text = self.clipboard_get()
            self.url_var.set(text.strip())
            self.url_entry.config(fg=self.colors["TEXT"])
        except tk.TclError:
            pass

    def _browse(self):
        folder = filedialog.askdirectory(initialdir=self.out_var.get())
        if folder:
            self.out_var.set(folder)

    def _start_download(self):
        if not self.ytdlp:
            self._warn_missing()
            return

        url = self.url_var.get().strip()
        if not url or url.startswith("https://youtube.com/watch?v=…"):
            messagebox.showwarning("No URL", "Please enter a URL to download.")
            return

        self._begin_run("Starting…")

        cmd = build_cmd(
            self.ytdlp,
            "audio",
            "Best",
            "mp3",
            self.out_var.get(),
            url,
            ffmpeg_dir=find_ffmpeg_dir(),
        )
        self._log(f"$ {' '.join(cmd)}\n")

        self._runner = DownloadRunner(
            cmd,
            on_line=lambda line: self.after(0, lambda l=line: self._log(l + "\n")),
            on_progress=self._on_progress,
            on_status=self._on_dl_status,
            on_done=self._on_done,
        )
        self._runner.start()

    def _stop_download(self):
        if self._runner:
            self._runner.stop()

    def _on_progress(self, pct, speed, eta):
        self.after(0, lambda: self._set_progress(pct))
        self.after(0, lambda: self._set_status(f"Downloading  {int(pct * 100)}%",
                                               self.colors["ACCENT"]))
        self.after(0, lambda: self.meta_var.set(f"{speed}  •  ETA {eta}"))

    def _on_dl_status(self, status):
        if status == "processing":
            self.after(0, lambda: self._set_status("Processing…", self.colors["TEXT_DIM"]))
        elif status == "downloading":
            self.after(0, lambda: self._set_status("Downloading…", self.colors["ACCENT"]))
        elif status == "splitting":
            self.after(0, lambda: self._set_status("Splitting…", self.colors["ACCENT"]))

    def _on_done(self, rc, exc=None):
        if exc:
            self.after(0, lambda: self._set_status(f"Error: {exc}", self.colors["RED"]))
        elif rc == 0:
            self.after(0, lambda: self._set_status("Done ✓", self.colors["GREEN"]))
            self.after(0, lambda: self._set_progress(1.0))
        elif rc == -15:
            self.after(0, lambda: self._set_status("Stopped", self.colors["MUTED"]))
        else:
            self.after(0, lambda: self._set_status(f"Error (exit {rc})", self.colors["RED"]))

        self.running = False
        self._runner = None

        def _restore_btns():
            self.dl_btn._disabled = False
            self.dl_btn.config(fg=self.colors["PRIMARY_FG"])
            self.stop_btn._disabled = True
            self.stop_btn.config(fg=self.colors["MUTED"])
        self.after(0, _restore_btns)

    # status
    def _set_progress(self, frac):
        self.progress_var.set(frac)
        self._redraw_bar()

    def _redraw_bar(self):
        w = self.progress_bar.winfo_width()
        frac = self.progress_var.get()
        fill_w = max(0, int(w * frac))
        self.progress_bar.coords(self._bar_fill, 0, 0, fill_w, 4)

    def _set_status(self, text, color=None):
        self.status_var.set(text)
        self.status_label.config(fg=color if color is not None else self.colors["TEXT_DIM"])

    # logs
    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _log_clear(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self._log_clear()
        self._set_status("Ready", self.colors["TEXT_DIM"])
        self._set_progress(0)
        self.meta_var.set("")

    # preferences
    def _save_prefs(self):
        self.prefs = {
            "last_url": self.url_var.get(),
            "out_dir":  self.out_var.get(),
            "tab":      self.tab_var.get(),
            "stems":    [label for label, var in self.stem_vars.items() if var.get()],
            "theme":    self.theme,
        }
        save_prefs(self.prefs_path, self.prefs)

    def _save_prefs_theme(self):
        self.prefs["theme"] = self.theme
        save_prefs(self.prefs_path, self.prefs)

    # misc
    def _ytdlp_version(self):
        if not self.ytdlp:
            return "yt-dlp not found"
        try:
            import subprocess
            r = subprocess.run([self.ytdlp, "--version"], capture_output=True, text=True)
            return f"{r.stdout.strip()}"
        except Exception:
            return ""

    def _warn_missing(self):
        messagebox.showwarning(
            "yt-dlp not found",
            "yt-dlp was not found on your system.\n\n"
            "Install it with:\n\n  brew install yt-dlp\n\n"
            "See the documentation for other options:\n"
            "https://github.com/yt-dlp/yt-dlp#installation"
        )

    def _warn_missing_demucs(self):
        messagebox.showwarning(
            "demucs not found",
            "demucs is needed for the Stem Splitter.\n\n"
            "Install it with:\n\n  uv tool install demucs --with numpy\n\n"
            "or:\n\n  pipx install demucs && pipx inject demucs numpy"
        )

    def _center(self):
        self.update_idletasks()
        w, h = 560, self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


# entry point
def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

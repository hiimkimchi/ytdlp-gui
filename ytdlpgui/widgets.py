import tkinter as tk
from tkinter import ttk
from .const import THEMES


class ThemeMixin:
    """Mixin that adds themed widget factories and live theme switching.

    Expects `self` to be a tk.Tk (or Toplevel) with:
      - self.theme: str          ("dark" | "light")
      - self.colors: dict        (copy of THEMES[self.theme])
    """

    def _init_theme(self):
        self._theme_widgets = []
        self._theme_toggle_btns = []
        self._theme_combobox_style = None

    # widget creators
    def _label(self, parent, text):
        c = self.colors
        lbl = tk.Label(parent, text=text, font=("Helvetica Neue", 9, "bold"),
                       fg=c["MUTED"], bg=c["BG"], anchor="w")
        lbl.pack(fill="x")
        self._theme_widgets.append((lbl, {"fg": "MUTED", "bg": "BG"}))

    def _entry(self, parent, var, placeholder=""):
        c = self.colors
        e = tk.Entry(parent, textvariable=var, bg=c["SURFACE"], fg=c["TEXT"],
                     insertbackground=c["ACCENT"], font=("Helvetica Neue", 13),
                     bd=0, highlightthickness=1, highlightbackground=c["BORDER"],
                     highlightcolor=c["ACCENT"], relief="flat")
        e.configure({"disabledforeground": c["TEXT_DIM"]})
        self._theme_widgets.append((e, {
            "bg": "SURFACE", "fg": "TEXT", "insertbackground": "ACCENT",
            "highlightbackground": "BORDER", "highlightcolor": "ACCENT",
            "disabledforeground": "TEXT_DIM",
        }))
        if placeholder and not var.get():
            e.insert(0, placeholder)
            e.config(fg=c["MUTED"])

            def _focus_in(ev):
                if e.get() == placeholder:
                    e.delete(0, "end")
                    e.config(fg=self.colors["TEXT"])

            def _focus_out(ev):
                if not e.get():
                    e.insert(0, placeholder)
                    e.config(fg=self.colors["MUTED"])

            e.bind("<FocusIn>", _focus_in)
            e.bind("<FocusOut>", _focus_out)
        return e

    def _btn(self, parent, text, cmd, style="default"):
        c = self.colors
        style_colors = {
            "primary": ("PRIMARY_BG", "PRIMARY_FG"),
            "danger":  ("BTN",        "RED"),
            "ghost":   ("BTN",        "TEXT_DIM"),
            "default": ("BTN",        "TEXT"),
        }
        bg_key, fg_key = style_colors[style]
        lbl = tk.Label(
            parent, text=text,
            bg=c[bg_key], fg=c[fg_key],
            font=("Helvetica Neue", 12, "bold" if style == "primary" else "normal"),
            padx=20, pady=10, cursor="hand2",
        )
        lbl.bind("<Button-1>", lambda e: cmd() if not getattr(lbl, "_disabled", False) else None)
        lbl._disabled = False
        self._theme_widgets.append((lbl, {"bg": bg_key, "fg": fg_key}))
        return lbl

    def _toggle_btn(self, parent, label, value, var, callback):
        c = self.colors
        lbl = tk.Label(
            parent, text=label,
            bg=c["BTN"], fg=c["TEXT_DIM"],
            font=("Helvetica Neue", 12), padx=14, pady=6, cursor="hand2",
        )

        def _refresh():
            cc = self.colors
            active = var.get() == value
            lbl.config(bg=cc["TOGGLE_ON"] if active else cc["BTN"],
                       fg=cc["TOGGLE_FG"] if active else cc["TEXT_DIM"])

        def _click(e):
            var.set(value)
            callback()
            _refresh()

        lbl.bind("<Button-1>", _click)
        _refresh()
        lbl.pack(side="left", padx=(0, 6))
        lbl._refresh = _refresh
        lbl._value = value
        if not hasattr(self, "_toggle_btns"):
            self._toggle_btns = []
        self._toggle_btns.append(lbl)
        self._theme_toggle_btns.append(lbl)

    def _dropdown(self, parent, var, options):
        c = self.colors
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("App.TCombobox",
                    fieldbackground=c["SURFACE"], background=c["SURFACE"],
                    foreground=c["TEXT"], bordercolor=c["BORDER"],
                    arrowcolor=c["TEXT_DIM"],
                    selectbackground=c["SURFACE"],
                    selectforeground=c["TEXT"],
                    padding=(6, 4))
        _map_combobox(s, c)
        cb = ttk.Combobox(parent, textvariable=var, values=options,
                          style="App.TCombobox", state="readonly",
                          font=("Helvetica Neue", 12))
        cb.pack(fill="x", pady=(4, 0))
        cb.bind("<<ComboboxSelected>>", lambda e: self.focus_set())
        self._theme_combobox_style = s
        return cb

    # theme state
    def _apply_theme(self):
        c = self.colors
        for item in self._theme_widgets:
            if len(item) == 3:
                w, canvas_id, opts = item
                for opt, key in opts.items():
                    w.itemconfig(canvas_id, **{opt: c[key]})
            else:
                w, opts = item
                for opt, key in opts.items():
                    try:
                        w[opt] = c[key]
                    except tk.TclError:
                        pass
        for btn in self._theme_toggle_btns:
            btn._refresh()
        if self._theme_combobox_style:
            s = self._theme_combobox_style
            s.configure("App.TCombobox",
                        fieldbackground=c["SURFACE"], background=c["SURFACE"],
                        foreground=c["TEXT"], bordercolor=c["BORDER"],
                        arrowcolor=c["TEXT_DIM"],
                        selectbackground=c["SURFACE"],
                        selectforeground=c["TEXT"])
            _map_combobox(s, c)
        self._theme_btn.config(text="☀" if self.theme == "dark" else "☽")
        self._redraw_bar()

    def _toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.colors = THEMES[self.theme].copy()
        self._save_prefs_theme()
        self._apply_theme()


def _map_combobox(style: ttk.Style, c: dict):
    """Apply combobox state map to suppress focus highlight."""
    style.map("App.TCombobox",
              fieldbackground=[("readonly focus", c["SURFACE"]),
                               ("readonly", c["SURFACE"]),
                               ("focus", c["SURFACE"])],
              selectbackground=[("readonly focus", c["SURFACE"]),
                                ("readonly", c["SURFACE"]),
                                ("focus", c["SURFACE"])],
              selectforeground=[("readonly focus", c["TEXT"]),
                                ("readonly", c["TEXT"]),
                                ("focus", c["TEXT"])],
              foreground=[("readonly focus", c["TEXT"]),
                          ("readonly", c["TEXT"]),
                          ("focus", c["TEXT"])],
              bordercolor=[("readonly focus", c["BORDER"]),
                           ("focus", c["BORDER"]),
                           ("readonly", c["BORDER"])])

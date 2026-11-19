import tkinter as tk
from tkinter import ttk

BG = "#0b1220"
PANEL = "#111c2e"
CARD = "#17243a"
TEXT = "#edf3fb"
MUTED = "#9aabc2"
ACCENT = "#39c6a5"
BLUE = "#4387f5"


def configure_style(root):
    root.configure(bg=BG)
    style = ttk.Style(root)
    try: style.theme_use("clam")
    except tk.TclError: pass
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("Card.TFrame", background=CARD)
    style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground=TEXT)
    style.configure("Sub.TLabel", foreground=MUTED, font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
    style.configure("CardValue.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 20, "bold"))
    style.configure("Accent.TButton", background=ACCENT, foreground="#07131a", padding=(12, 8), borderwidth=0, font=("Segoe UI", 10, "bold"))
    style.map("Accent.TButton", background=[("active", "#65dfc2")])
    style.configure("Nav.TButton", background=PANEL, foreground=TEXT, padding=(14, 10), anchor="w", borderwidth=0)
    style.map("Nav.TButton", background=[("active", CARD)])
    style.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT, rowheight=30, borderwidth=0)
    style.configure("Treeview.Heading", background=PANEL, foreground=TEXT, font=("Segoe UI", 9, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", "#245b68")])
    style.configure("TEntry", padding=7)
    style.configure("TCombobox", padding=6)

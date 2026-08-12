from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import urllib.request
from collections import defaultdict
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk

import psutil

APP_NAME = "NightOwl Utilities"
VERSION = "1.0.0"
APP_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "NightOwlUtilities"
CONFIG_PATH = APP_DIR / "config.json"

BG, PANEL, CARD = "#0b0f17", "#111827", "#182235"
TEXT, MUTED, ACCENT, GOOD, WARN, BAD = "#ecf3ff", "#94a3b8", "#5eead4", "#34d399", "#fbbf24", "#fb7185"


def fmt_size(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"github_repo": "OWNER/REPOSITORY", "downloads": str(Path.home() / "Downloads")}


def save_config(config: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


class NightOwl(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}  •  v{VERSION}")
        self.geometry("1180x760")
        self.minsize(980, 640)
        self.configure(bg=BG)
        self.config_data = load_config()
        self._style()
        self._layout()
        self.show_dashboard()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 23), foreground=TEXT)
        style.configure("Sub.TLabel", foreground=MUTED)
        style.configure("CardTitle.TLabel", background=CARD, font=("Segoe UI Semibold", 11), foreground=MUTED)
        style.configure("CardValue.TLabel", background=CARD, font=("Segoe UI Semibold", 21), foreground=TEXT)
        style.configure("Nav.TButton", background=PANEL, foreground=MUTED, borderwidth=0, padding=(18, 13), anchor="w")
        style.map("Nav.TButton", background=[("active", CARD)], foreground=[("active", TEXT)])
        style.configure("Accent.TButton", background=ACCENT, foreground="#06201d", borderwidth=0, padding=(14, 9), font=("Segoe UI Semibold", 10))
        style.map("Accent.TButton", background=[("active", "#99f6e4")])
        style.configure("TButton", background=CARD, foreground=TEXT, borderwidth=0, padding=(12, 8))
        style.map("TButton", background=[("active", "#24324a")])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background=CARD, foreground=TEXT, borderwidth=0)
        style.map("Treeview", background=[("selected", "#164e63")])
        style.configure("TEntry", fieldbackground=CARD, foreground=TEXT, insertcolor=TEXT, borderwidth=0, padding=8)
        style.configure("Horizontal.TProgressbar", troughcolor=CARD, background=ACCENT, borderwidth=0)

    def _layout(self):
        sidebar = ttk.Frame(self, style="Panel.TFrame", width=215)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="NIGHTOWL", bg=PANEL, fg=ACCENT, font=("Segoe UI Semibold", 18)).pack(anchor="w", padx=20, pady=(24, 4))
        tk.Label(sidebar, text="WINDOWS UTILITIES", bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=21, pady=(0, 24))
        for text, command in [
            ("Dashboard", self.show_dashboard), ("Storage", self.show_storage),
            ("Large files", self.show_large_files), ("Duplicates", self.show_duplicates),
            ("Downloads", self.show_organizer), ("Defender", self.show_defender),
            ("Updates", self.show_updates),
        ]:
            ttk.Button(sidebar, text=text, command=command, style="Nav.TButton").pack(fill="x")
        tk.Label(sidebar, text=f"v{VERSION}", bg=PANEL, fg=MUTED).pack(side="bottom", anchor="w", padx=20, pady=18)
        self.content = ttk.Frame(self)
        self.content.pack(side="left", fill="both", expand=True, padx=28, pady=24)

    def clear(self):
        for child in self.content.winfo_children():
            child.destroy()

    def heading(self, title: str, subtitle: str):
        ttk.Label(self.content, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.content, text=subtitle, style="Sub.TLabel").pack(anchor="w", pady=(2, 20))

    def card(self, parent, title: str, value: str):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=18)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 12))
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(frame, text=value, style="CardValue.TLabel").pack(anchor="w", pady=(8, 0))

    def run_thread(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    def show_dashboard(self):
        self.clear(); self.heading("Dashboard", "A quick look at this computer")
        cpu, mem = psutil.cpu_percent(interval=.15), psutil.virtual_memory()
        row = ttk.Frame(self.content); row.pack(fill="x")
        self.card(row, "CPU", f"{cpu:.0f}%")
        self.card(row, "MEMORY", f"{mem.percent:.0f}%")
        self.card(row, "AVAILABLE RAM", fmt_size(mem.available))
        self.card(row, "SYSTEM", platform.system() + " " + platform.release())
        ttk.Label(self.content, text="DRIVES", style="Sub.TLabel").pack(anchor="w", pady=(26, 10))
        for part in psutil.disk_partitions(all=False):
            try: usage = psutil.disk_usage(part.mountpoint)
            except (PermissionError, OSError): continue
            box = ttk.Frame(self.content, style="Card.TFrame", padding=16); box.pack(fill="x", pady=5)
            ttk.Label(box, text=f"{part.device}  {fmt_size(usage.used)} used of {fmt_size(usage.total)}", style="CardTitle.TLabel").pack(anchor="w")
            bar = ttk.Progressbar(box, maximum=100, value=usage.percent); bar.pack(fill="x", pady=(10, 0))

    def show_storage(self):
        self.clear(); self.heading("Storage", "Mounted drives and free space")
        tree = ttk.Treeview(self.content, columns=("type", "total", "used", "free", "percent"), show="headings")
        for col, width in [("type", 130), ("total", 130), ("used", 130), ("free", 130), ("percent", 100)]:
            tree.heading(col, text=col.upper()); tree.column(col, width=width)
        tree.pack(fill="both", expand=True)
        for part in psutil.disk_partitions(all=False):
            try: u = psutil.disk_usage(part.mountpoint)
            except (OSError, PermissionError): continue
            tree.insert("", "end", text=part.device, values=(f"{part.device} {part.fstype}", fmt_size(u.total), fmt_size(u.used), fmt_size(u.free), f"{u.percent}%"))

    def folder_picker(self, default=None):
        row = ttk.Frame(self.content); row.pack(fill="x", pady=(0, 12))
        value = tk.StringVar(value=str(default or Path.home()))
        ttk.Entry(row, textvariable=value).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", command=lambda: value.set(filedialog.askdirectory() or value.get())).pack(side="left", padx=(8, 0))
        return value, row

    def results_tree(self, columns):
        tree = ttk.Treeview(self.content, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col.upper()); tree.column(col, width=160 if col != "path" else 560)
        tree.pack(fill="both", expand=True, pady=(8, 0)); return tree

    def show_large_files(self):
        self.clear(); self.heading("Large files", "Find space hogs without deleting anything")
        folder, row = self.folder_picker()
        ttk.Button(row, text="Scan", style="Accent.TButton", command=lambda: self.scan_large(Path(folder.get()), tree, status)).pack(side="left", padx=8)
        status = ttk.Label(self.content, text="Choose a folder and scan.", style="Sub.TLabel"); status.pack(anchor="w")
        tree = self.results_tree(("size", "path"))

    def scan_large(self, folder, tree, status):
        tree.delete(*tree.get_children()); status.config(text="Scanning…")
        def work():
            found=[]
            for root, _, names in os.walk(folder):
                for name in names:
                    path=Path(root)/name
                    try: found.append((path.stat().st_size, str(path)))
                    except OSError: pass
            found.sort(reverse=True)
            self.after(0, lambda: [tree.insert("", "end", values=(fmt_size(s), p)) for s,p in found[:250]])
            self.after(0, lambda: status.config(text=f"Showing the 250 largest of {len(found):,} files."))
        self.run_thread(work)

    def show_duplicates(self):
        self.clear(); self.heading("Duplicates", "Hash files to find exact duplicate content")
        folder, row = self.folder_picker()
        ttk.Button(row, text="Find duplicates", style="Accent.TButton", command=lambda: self.scan_duplicates(Path(folder.get()), tree, status)).pack(side="left", padx=8)
        status=ttk.Label(self.content,text="No files have been scanned.",style="Sub.TLabel"); status.pack(anchor="w")
        tree=self.results_tree(("group", "size", "path"))

    def scan_duplicates(self, folder, tree, status):
        tree.delete(*tree.get_children()); status.config(text="Grouping files by size…")
        def work():
            sizes=defaultdict(list)
            for root, _, names in os.walk(folder):
                for name in names:
                    path=Path(root)/name
                    try:
                        size=path.stat().st_size
                        if size: sizes[size].append(path)
                    except OSError: pass
            hashes=defaultdict(list)
            candidates=[p for paths in sizes.values() if len(paths)>1 for p in paths]
            for i,path in enumerate(candidates,1):
                try: hashes[(path.stat().st_size,file_hash(path))].append(path)
                except OSError: pass
                if i%10==0: self.after(0,lambda i=i: status.config(text=f"Hashing {i:,} of {len(candidates):,} candidates…"))
            groups=[(key,paths) for key,paths in hashes.items() if len(paths)>1]
            def render():
                for number,((size,_),paths) in enumerate(groups,1):
                    for path in paths: tree.insert("","end",values=(number,fmt_size(size),str(path)))
                wasted=sum(size*(len(paths)-1) for (size,_),paths in groups)
                status.config(text=f"{len(groups)} duplicate groups • up to {fmt_size(wasted)} recoverable. Review before deleting.")
            self.after(0,render)
        self.run_thread(work)

    def show_organizer(self):
        self.clear(); self.heading("Downloads organizer", "Preview and sort loose files into category folders")
        folder,row=self.folder_picker(self.config_data.get("downloads",Path.home()/"Downloads"))
        ttk.Button(row,text="Preview",command=lambda:self.preview_organize(Path(folder.get()),tree)).pack(side="left",padx=8)
        ttk.Button(row,text="Apply moves",style="Accent.TButton",command=lambda:self.apply_organize(Path(folder.get()),tree)).pack(side="left")
        tree=self.results_tree(("category","path"))

    def organize_plan(self, folder):
        groups={"Images":{'.png','.jpg','.jpeg','.gif','.webp','.bmp'},"Documents":{'.pdf','.txt','.doc','.docx','.xls','.xlsx','.ppt','.pptx'},"Archives":{'.zip','.rar','.7z','.tar','.gz'},"Installers":{'.exe','.msi','.msix'},"Code":{'.py','.js','.ts','.json','.html','.css','.ps1'}}
        plan=[]
        try: items=list(folder.iterdir())
        except OSError: return plan
        for path in items:
            if not path.is_file(): continue
            category=next((name for name,exts in groups.items() if path.suffix.lower() in exts),"Other")
            plan.append((path,category))
        return plan

    def preview_organize(self,folder,tree):
        tree.delete(*tree.get_children())
        for path,cat in self.organize_plan(folder): tree.insert("","end",values=(cat,str(path)))

    def apply_organize(self,folder,tree):
        plan=self.organize_plan(folder)
        if not plan or not messagebox.askyesno("Confirm moves",f"Move {len(plan)} loose files into category folders?\n\nExisting files will never be overwritten."): return
        moved=0
        for path,cat in plan:
            target=folder/cat/path.name
            try:
                target.parent.mkdir(exist_ok=True)
                if not target.exists(): shutil.move(str(path),str(target)); moved+=1
            except OSError: pass
        self.preview_organize(folder,tree); messagebox.showinfo("Finished",f"Moved {moved} files.")

    def show_defender(self):
        self.clear(); self.heading("Microsoft Defender", "Use Windows' maintained antivirus engine")
        folder,row=self.folder_picker(Path.home()/"Downloads")
        output=tk.Text(self.content,bg=PANEL,fg=TEXT,insertbackground=TEXT,relief="flat",font=("Cascadia Mono",10),padx=12,pady=12); output.pack(fill="both",expand=True,pady=12)
        def run_scan():
            path=str(Path(folder.get()))
            if not messagebox.askyesno("Start scan",f"Ask Microsoft Defender to scan:\n{path}? "): return
            output.delete("1.0","end"); output.insert("end","Updating signatures and starting scan…\n")
            def work():
                command=f"Update-MpSignature; Start-MpScan -ScanType CustomScan -ScanPath '{path.replace(chr(39),chr(39)*2)}'; Get-MpThreatDetection | Select InitialDetectionTime,ThreatID,ActionSuccess,Resources | Format-List"
                result=subprocess.run(["powershell.exe","-NoProfile","-Command",command],capture_output=True,text=True,creationflags=0x08000000)
                text=result.stdout or result.stderr or "Scan completed. No detections were returned."
                self.after(0,lambda: output.insert("end",text))
            self.run_thread(work)
        ttk.Button(row,text="Scan with Defender",style="Accent.TButton",command=run_scan).pack(side="left",padx=8)

    def show_updates(self):
        self.clear(); self.heading("Updates", "Signed-by-hash releases from your GitHub repository")
        repo=tk.StringVar(value=self.config_data.get("github_repo","OWNER/REPOSITORY"))
        ttk.Label(self.content,text="GitHub repository (owner/name)",style="Sub.TLabel").pack(anchor="w")
        ttk.Entry(self.content,textvariable=repo).pack(fill="x",pady=(6,12))
        status=ttk.Label(self.content,text=f"Installed version: {VERSION}",style="Sub.TLabel"); status.pack(anchor="w",pady=10)
        def check():
            slug=repo.get().strip().strip('/')
            if '/' not in slug or slug.startswith("OWNER/"): messagebox.showwarning("Repository needed","Enter your GitHub username and repository, such as sebas/nightowl-utilities."); return
            self.config_data["github_repo"]=slug; save_config(self.config_data); status.config(text="Checking for updates…")
            def work():
                try:
                    url=f"https://raw.githubusercontent.com/{slug}/main/latest.json"
                    with urllib.request.urlopen(url,timeout=12) as response: manifest=json.load(response)
                    latest=str(manifest["version"])
                    self.after(0,lambda: status.config(text=f"Installed: {VERSION} • Available: {latest}"))
                    if tuple(map(int,latest.split('.'))) > tuple(map(int,VERSION.split('.'))): self.after(0,lambda:self.offer_update(manifest))
                    else: self.after(0,lambda:messagebox.showinfo("Up to date",f"{APP_NAME} {VERSION} is current."))
                except Exception as exc: self.after(0,lambda:status.config(text=f"Update check failed: {exc}"))
            self.run_thread(work)
        ttk.Button(self.content,text="Save and check",style="Accent.TButton",command=check).pack(anchor="w")

    def offer_update(self,manifest):
        if not getattr(sys,"frozen",False): messagebox.showinfo("Update available",f"Version {manifest['version']} is available. Automatic replacement works in the packaged EXE."); return
        if not messagebox.askyesno("Update available",f"Install version {manifest['version']} now?"): return
        def work():
            try:
                APP_DIR.mkdir(parents=True,exist_ok=True); new=APP_DIR/"NightOwlUtilities.new.exe"
                urllib.request.urlretrieve(manifest["url"],new)
                if file_hash(new).lower()!=str(manifest["sha256"]).lower(): new.unlink(missing_ok=True); raise ValueError("download hash did not match")
                current=Path(sys.executable); script=APP_DIR/"finish-update.cmd"
                script.write_text(f'@echo off\ntimeout /t 2 /nobreak >nul\ncopy /y "{new}" "{current}" >nul\nstart "" "{current}"\ndel "%~f0"\n',encoding="utf-8")
                subprocess.Popen(["cmd.exe","/c",str(script)],creationflags=0x08000000); self.after(0,self.destroy)
            except Exception as exc: self.after(0,lambda:messagebox.showerror("Update failed",str(exc)))
        self.run_thread(work)


if __name__ == "__main__":
    NightOwl().mainloop()

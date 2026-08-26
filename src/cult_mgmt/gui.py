"""Tk desktop interface for the Cultivation Management Suite."""

from __future__ import annotations

import tkinter as tk
import calendar
from datetime import date
from tkinter import messagebox, ttk
from typing import Callable

from cult_mgmt.app_data import CultivationStore, DataError


BG = "#f3f5f0"
SURFACE = "#ffffff"
INK = "#17221b"
MUTED = "#647168"
GREEN = "#245c3a"
GREEN_2 = "#347a4d"
PALE = "#dce9df"
RED = "#a63d40"
GOLD = "#a87018"
PHASE_COLORS = {"clone": "#7d62a9", "veg": "#347a4d", "flower": "#b17b20", "dry": "#8a6245"}


class FormDialog(tk.Toplevel):
    def __init__(self, parent, title: str, fields: list[dict], on_save: Callable[[dict], None]):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=SURFACE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save
        self.inputs: dict[str, tk.Widget] = {}

        shell = ttk.Frame(self, style="Card.TFrame", padding=28)
        shell.grid(sticky="nsew")
        ttk.Label(shell, text=title, style="DialogTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        for row, field in enumerate(fields, 1):
            ttk.Label(shell, text=field["label"], style="Form.TLabel").grid(row=row, column=0, sticky="w", padx=(0, 18), pady=7)
            if field.get("type") == "choice":
                widget = ttk.Combobox(shell, values=field["values"], state="readonly", width=30)
            else:
                widget = ttk.Entry(shell, width=33)
            widget.grid(row=row, column=1, sticky="ew", pady=7)
            value = field.get("value", "")
            if value is not None:
                if isinstance(widget, ttk.Combobox):
                    widget.set(str(value))
                else:
                    widget.insert(0, str(value))
            self.inputs[field["key"]] = widget

        buttons = ttk.Frame(shell, style="Card.TFrame")
        buttons.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="e", pady=(22, 0))
        ttk.Button(buttons, text="Cancel", style="Quiet.TButton", command=self.destroy).pack(side="left", padx=6)
        ttk.Button(buttons, text="Save", style="Primary.TButton", command=self.save).pack(side="left")
        self.bind("<Return>", lambda _e: self.save())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 20)}+{max(y, 20)}")
        next(iter(self.inputs.values())).focus_set()

    def save(self):
        values = {key: widget.get().strip() for key, widget in self.inputs.items()}
        try:
            self.on_save(values)
        except (DataError, ValueError) as exc:
            messagebox.showerror("Couldn't save", str(exc), parent=self)
            return
        self.destroy()


class CultivationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.store = CultivationStore()
        self.title("Cultivation Management Suite")
        self.geometry("1240x780")
        self.minsize(1050, 680)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._style()
        self.pages: dict[str, ttk.Frame] = {}
        self.nav_buttons: dict[str, ttk.Button] = {}
        self.calendar_month = date.today().replace(day=1)
        self._layout()
        self.show_page("Dashboard")

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("DejaVu Sans", 10), foreground=INK)
        style.configure("App.TFrame", background=BG)
        style.configure("Card.TFrame", background=SURFACE)
        style.configure("Sidebar.TFrame", background="#183425")
        style.configure("Brand.TLabel", background="#183425", foreground="white", font=("DejaVu Sans", 16, "bold"))
        style.configure("BrandSub.TLabel", background="#183425", foreground="#a9bdae", font=("DejaVu Sans", 9))
        style.configure("Nav.TButton", background="#183425", foreground="#dbe7de", anchor="w", padding=(20, 12), borderwidth=0)
        style.map("Nav.TButton", background=[("active", "#24543a")], foreground=[("active", "white")])
        style.configure("NavActive.TButton", background="#2e6946", foreground="white", anchor="w", padding=(20, 12), borderwidth=0)
        style.configure("Title.TLabel", background=BG, foreground=INK, font=("DejaVu Sans", 24, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("DejaVu Sans", 10))
        style.configure("CardTitle.TLabel", background=SURFACE, foreground=MUTED, font=("DejaVu Sans", 9, "bold"))
        style.configure("Metric.TLabel", background=SURFACE, foreground=INK, font=("DejaVu Sans", 25, "bold"))
        style.configure("DialogTitle.TLabel", background=SURFACE, foreground=INK, font=("DejaVu Sans", 17, "bold"))
        style.configure("Form.TLabel", background=SURFACE, foreground=INK)
        style.configure("Primary.TButton", background=GREEN, foreground="white", padding=(16, 9), borderwidth=0)
        style.map("Primary.TButton", background=[("active", GREEN_2)])
        style.configure("Quiet.TButton", background="#e9ede8", foreground=INK, padding=(14, 9), borderwidth=0)
        style.map("Quiet.TButton", background=[("active", "#dce3dc")])
        style.configure("Danger.TButton", background="#f4dfdf", foreground=RED, padding=(14, 9), borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#eccccc")])
        style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE, foreground=INK, rowheight=42, borderwidth=0)
        style.configure("Treeview.Heading", background="#e8ede8", foreground="#3e4c43", font=("DejaVu Sans", 9, "bold"), padding=10, borderwidth=0)
        style.map("Treeview", background=[("selected", PALE)], foreground=[("selected", INK)])
        style.configure("TEntry", padding=7, fieldbackground="white")
        style.configure("TCombobox", padding=7, fieldbackground="white")
        style.configure("TCheckbutton", background=BG)

    def _layout(self):
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=215)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        brand = ttk.Frame(sidebar, style="Sidebar.TFrame", padding=(20, 24))
        brand.pack(fill="x")
        ttk.Label(brand, text="CULTIVATE", style="Brand.TLabel").pack(anchor="w")
        ttk.Label(brand, text="MANAGEMENT SUITE", style="BrandSub.TLabel").pack(anchor="w", pady=(2, 18))
        for name, symbol in [("Dashboard", "⌂"), ("Rooms", "▦"), ("Batches", "◉"), ("Tasks", "✓"), ("Calendar", "□"), ("Strains", "♢"), ("Settings", "⚙")]:
            button = ttk.Button(sidebar, text=f"{symbol}   {name}", style="Nav.TButton", command=lambda n=name: self.show_page(n))
            button.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[name] = button
        ttk.Label(sidebar, text="PostgreSQL • Desktop", style="BrandSub.TLabel").pack(side="bottom", anchor="w", padx=20, pady=20)

        self.content = ttk.Frame(self, style="App.TFrame", padding=(34, 26))
        self.content.pack(side="left", fill="both", expand=True)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        for name in self.nav_buttons:
            page = ttk.Frame(self.content, style="App.TFrame")
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = page

    def show_page(self, name: str):
        for nav_name, button in self.nav_buttons.items():
            button.configure(style="NavActive.TButton" if nav_name == name else "Nav.TButton")
        page = self.pages[name]
        for child in page.winfo_children():
            child.destroy()
        builders = {
            "Dashboard": self.dashboard_page, "Rooms": self.rooms_page,
            "Batches": self.batches_page, "Tasks": self.tasks_page,
            "Calendar": self.calendar_page,
            "Strains": self.strains_page, "Settings": self.settings_page,
        }
        try:
            builders[name](page)
        except DataError as exc:
            self.error_page(page, exc)
        page.tkraise()

    def error_page(self, page, exc: Exception):
        self.header(page, "Connection needed", "Your data is safe. The app just couldn't reach PostgreSQL.")
        card = ttk.Frame(page, style="Card.TFrame", padding=28)
        card.pack(fill="x", pady=24)
        ttk.Label(card, text="Database unavailable", style="DialogTitle.TLabel").pack(anchor="w")
        ttk.Label(card, text=str(exc), style="Form.TLabel", wraplength=700).pack(anchor="w", pady=(10, 18))
        ttk.Button(card, text="Try again", style="Primary.TButton", command=lambda: self.show_page("Dashboard")).pack(anchor="w")

    def header(self, page, title: str, subtitle: str, action: str | None = None, command=None):
        row = ttk.Frame(page, style="App.TFrame")
        row.pack(fill="x", pady=(0, 22))
        left = ttk.Frame(row, style="App.TFrame")
        left.pack(side="left")
        ttk.Label(left, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(left, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))
        if action:
            ttk.Button(row, text=action, style="Primary.TButton", command=command).pack(side="right", pady=5)

    def table(self, parent, columns: list[tuple[str, str, int]]) -> ttk.Treeview:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=1)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings", selectmode="browse")
        for key, label, width in columns:
            tree.heading(key, text=label)
            tree.column(key, width=width, minwidth=60, anchor="w", stretch=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def selected(self, tree: ttk.Treeview) -> dict | None:
        selection = tree.selection()
        return getattr(tree, "records", {}).get(selection[0]) if selection else None

    def confirm_delete(self, noun: str, callback: Callable[[], None]):
        if messagebox.askyesno(f"Delete {noun}?", f"This will permanently delete the selected {noun}.", icon="warning"):
            try:
                callback()
            except DataError as exc:
                messagebox.showerror("Couldn't delete", str(exc))

    # Pages
    def dashboard_page(self, page):
        facility = self.store.facility()
        title = facility["name"] if facility else "Your facility"
        self.header(page, title, f"Cultivation overview • {date.today().strftime('%A, %B %d')}")
        stats = self.store.dashboard()
        metrics = [("ACTIVE BATCHES", stats.get("active_batches", 0)), ("TOTAL PLANTS", stats.get("plants", 0)),
                   ("ROOMS", stats.get("rooms", 0)), ("OPEN TASKS", stats.get("open_tasks", 0))]
        strip = ttk.Frame(page, style="App.TFrame")
        strip.pack(fill="x")
        for i, (label, value) in enumerate(metrics):
            strip.columnconfigure(i, weight=1)
            card = ttk.Frame(strip, style="Card.TFrame", padding=20)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 0 if i == 3 else 7))
            ttk.Label(card, text=label, style="CardTitle.TLabel").pack(anchor="w")
            ttk.Label(card, text=str(value), style="Metric.TLabel").pack(anchor="w", pady=(6, 0))
        body = ttk.Frame(page, style="App.TFrame")
        body.pack(fill="both", expand=True, pady=(22, 0))
        body.columnconfigure(0, weight=3); body.columnconfigure(1, weight=2); body.rowconfigure(0, weight=1)
        room_card = ttk.Frame(body, style="Card.TFrame", padding=22)
        room_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(room_card, text="ROOM STATUS", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 12))
        rooms = self.store.rooms()
        if not rooms:
            ttk.Label(room_card, text="No rooms yet. Add your first room to get started.", style="Form.TLabel").pack(anchor="w", pady=20)
        for room in rooms:
            line = ttk.Frame(room_card, style="Card.TFrame")
            line.pack(fill="x", pady=7)
            dot = tk.Label(line, text="●", bg=SURFACE, fg=PHASE_COLORS.get(room["room_type"], MUTED), font=("DejaVu Sans", 13))
            dot.pack(side="left", padx=(0, 10))
            ttk.Label(line, text=room["name"], style="Form.TLabel", width=22).pack(side="left")
            ttk.Label(line, text=room["room_type"].upper(), style="CardTitle.TLabel").pack(side="left")
            ttk.Label(line, text=f"{room['plants']} plants", style="Form.TLabel").pack(side="right")
        task_card = ttk.Frame(body, style="Card.TFrame", padding=22)
        task_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ttk.Label(task_card, text="NEXT UP", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 12))
        tasks = self.store.tasks()[:7]
        if not tasks:
            ttk.Label(task_card, text="Nothing due. Nice work.", style="Form.TLabel").pack(anchor="w", pady=20)
        for task in tasks:
            line = ttk.Frame(task_card, style="Card.TFrame")
            line.pack(fill="x", pady=8)
            ttk.Label(line, text=task["name"], style="Form.TLabel").pack(anchor="w")
            due = task["due_date"].strftime("%b %d") if task["due_date"] else "No date"
            label = f"{task['room'] or '—'}  •  {due}"
            tk.Label(line, text=label, bg=SURFACE, fg=RED if task["overdue"] else MUTED, font=("DejaVu Sans", 9)).pack(anchor="w", pady=(2, 0))

    def rooms_page(self, page):
        self.header(page, "Rooms", "Capacity and current cultivation activity", "+ Add room", lambda: self.room_dialog())
        tree = self.table(page, [("name", "ROOM", 230), ("type", "PHASE", 140), ("batches", "BATCHES", 110), ("plants", "PLANTS", 110)])
        tree.records = {}
        for room in self.store.rooms():
            iid = tree.insert("", "end", values=(room["name"], room["room_type"].title(), room["batches"], room["plants"]))
            tree.records[iid] = room
        controls = ttk.Frame(page, style="App.TFrame"); controls.pack(fill="x", pady=(14, 0))
        ttk.Button(controls, text="Edit", style="Quiet.TButton", command=lambda: self.room_dialog(self.selected(tree))).pack(side="left")
        ttk.Button(controls, text="Delete", style="Danger.TButton", command=lambda: self.delete_room(self.selected(tree))).pack(side="left", padx=8)

    def room_dialog(self, room=None):
        if room is None and room is not False: room = room
        FormDialog(self, "Edit room" if room else "Add room", [
            {"key":"name", "label":"Room name", "value":room["name"] if room else ""},
            {"key":"type", "label":"Room phase", "type":"choice", "values":["clone","veg","flower","dry"], "value":room["room_type"] if room else "clone"},
        ], lambda v: (self._require(v["name"], "Room name"), self.store.save_room(v["name"], v["type"], room["id"] if room else None), self.show_page("Rooms")))

    def delete_room(self, room):
        if not room: return
        self.confirm_delete("room", lambda: (self.store.delete_room(room["id"]), self.show_page("Rooms")))

    def strains_page(self, page):
        self.header(page, "Strains", "Your reusable cultivar library", "+ Add strain", lambda: self.strain_dialog())
        tree = self.table(page, [("name", "STRAIN", 360), ("batches", "ALL-TIME BATCHES", 170), ("plants", "ACTIVE PLANTS", 150)])
        tree.records = {}
        for strain in self.store.strains():
            iid = tree.insert("", "end", values=(strain["name"], strain["batches"], strain["plants"])); tree.records[iid] = strain
        controls = ttk.Frame(page, style="App.TFrame"); controls.pack(fill="x", pady=(14, 0))
        ttk.Button(controls, text="Rename", style="Quiet.TButton", command=lambda: self.strain_dialog(self.selected(tree))).pack(side="left")
        ttk.Button(controls, text="Delete", style="Danger.TButton", command=lambda: self.delete_strain(self.selected(tree))).pack(side="left", padx=8)

    def strain_dialog(self, strain=None):
        FormDialog(self, "Rename strain" if strain else "Add strain", [{"key":"name", "label":"Strain name", "value":strain["name"] if strain else ""}],
                   lambda v: (self._require(v["name"], "Strain name"), self.store.save_strain(v["name"], strain["id"] if strain else None), self.show_page("Strains")))

    def delete_strain(self, strain):
        if strain: self.confirm_delete("strain", lambda: (self.store.delete_strain(strain["id"]), self.show_page("Strains")))

    def batches_page(self, page):
        show_all = tk.BooleanVar(value=False)
        self.header(page, "Batches", "Track plants from clone through harvest", "+ Add batch", lambda: self.batch_dialog())
        filter_row = ttk.Frame(page, style="App.TFrame"); filter_row.pack(fill="x", pady=(0, 10))
        ttk.Checkbutton(filter_row, text="Show completed", variable=show_all, command=lambda: fill()).pack(side="right")
        tree = self.table(page, [("name","BATCH",190),("strain","STRAIN",190),("room","ROOM",150),("phase","PHASE",100),("plants","PLANTS",85),("day","DAY",75),("status","STATUS",100)])
        tree.records = {}
        def fill():
            for iid in tree.get_children(): tree.delete(iid)
            tree.records = {}
            for batch in self.store.batches(show_all.get()):
                iid=tree.insert("","end",values=(batch["name"],batch["strain"] or "—",batch["room"] or "—",(batch["phase"] or "—").title(),batch["plant_count"],batch["phase_day"] or "—",batch["status"].title()))
                tree.records[iid]=batch
        fill()
        controls=ttk.Frame(page,style="App.TFrame"); controls.pack(fill="x",pady=(14,0))
        ttk.Button(controls,text="Edit",style="Quiet.TButton",command=lambda:self.batch_dialog(self.selected(tree))).pack(side="left")
        ttk.Button(controls,text="Move",style="Primary.TButton",command=lambda:self.move_dialog(self.selected(tree))).pack(side="left",padx=8)
        ttk.Button(controls,text="Harvest",style="Quiet.TButton",command=lambda:self.batch_action(self.selected(tree),"harvest")).pack(side="left")
        ttk.Button(controls,text="Finish",style="Quiet.TButton",command=lambda:self.batch_action(self.selected(tree),"finish")).pack(side="left",padx=8)
        ttk.Button(controls,text="Delete",style="Danger.TButton",command=lambda:self.batch_action(self.selected(tree),"delete")).pack(side="right")

    def batch_dialog(self,batch=None):
        rooms=self.store.rooms(); strains=self.store.strains()
        if not rooms or not strains:
            messagebox.showinfo("Set up required","Add at least one room and one strain before creating a batch."); return
        room_names=[r["name"] for r in rooms]; strain_names=[s["name"] for s in strains]
        fields=[{"key":"name","label":"Batch name","value":batch["name"] if batch else ""},
                {"key":"strain","label":"Strain","type":"choice","values":strain_names,"value":batch["strain"] if batch else strain_names[0]},
                {"key":"room","label":"Room","type":"choice","values":room_names,"value":batch["room"] if batch else room_names[0]},
                {"key":"count","label":"Plant count","value":batch["plant_count"] if batch else ""}]
        def save(v):
            self._require(v["name"],"Batch name"); count=int(v["count"])
            sid=next(s["id"] for s in strains if s["name"]==v["strain"]); rid=next(r["id"] for r in rooms if r["name"]==v["room"])
            self.store.save_batch(v["name"],sid,rid,count,batch["id"] if batch else None); self.show_page("Batches")
        FormDialog(self,"Edit batch" if batch else "Add batch",fields,save)

    def move_dialog(self,batch):
        if not batch:return
        rooms=self.store.rooms(); names=[r["name"] for r in rooms]
        FormDialog(self,f"Move {batch['name']}",[{"key":"room","label":"Destination","type":"choice","values":names,"value":batch["room"]}],
                   lambda v:(self.store.move_batch(batch["id"],next(r["id"] for r in rooms if r["name"]==v["room"])),self.show_page("Batches")))

    def batch_action(self,batch,action):
        if not batch:return
        try:
            if action=="harvest":
                if messagebox.askyesno("Harvest batch?",f"Move {batch['name']} to dry and record today's harvest date?"):
                    self.store.harvest_batch(batch["id"])
            elif action=="finish":
                if messagebox.askyesno("Finish batch?",f"Mark {batch['name']} completed?"): self.store.finish_batch(batch["id"])
            else:
                self.confirm_delete("batch",lambda:(self.store.delete_batch(batch["id"]),self.show_page("Batches"))); return
            self.show_page("Batches")
        except DataError as exc: messagebox.showerror("Action failed",str(exc))

    def tasks_page(self,page):
        show_all=tk.BooleanVar(value=False)
        self.header(page,"Tasks","Work due across every room and batch","+ Add task",lambda:self.task_dialog())
        filters=ttk.Frame(page,style="App.TFrame"); filters.pack(fill="x",pady=(0,10))
        ttk.Checkbutton(filters,text="Show completed",variable=show_all,command=lambda:fill()).pack(side="right")
        tree=self.table(page,[("task","TASK",260),("due","DUE",115),("room","ROOM",145),("batch","BATCH",165),("status","STATUS",115)])
        tree.tag_configure("overdue",foreground=RED); tree.tag_configure("done",foreground=MUTED); tree.records={}
        def fill():
            for iid in tree.get_children():tree.delete(iid)
            tree.records={}
            for task in self.store.tasks(show_all.get()):
                status="Complete" if task["completed"] else ("Overdue" if task["overdue"] else "Open")
                iid=tree.insert("","end",values=(task["name"],task["due_date"] or "—",task["room"] or "—",task["batch"] or "—",status),tags=("done" if task["completed"] else "overdue" if task["overdue"] else "",));tree.records[iid]=task
        fill(); controls=ttk.Frame(page,style="App.TFrame");controls.pack(fill="x",pady=(14,0))
        ttk.Button(controls,text="Edit",style="Quiet.TButton",command=lambda:self.task_dialog(self.selected(tree))).pack(side="left")
        ttk.Button(controls,text="Mark complete",style="Primary.TButton",command=lambda:self.task_complete(self.selected(tree))).pack(side="left",padx=8)
        ttk.Button(controls,text="Delete",style="Danger.TButton",command=lambda:self.task_delete(self.selected(tree))).pack(side="right")

    def calendar_page(self, page):
        month = self.calendar_month
        self.header(page, "Calendar", "A monthly view of scheduled cultivation work", "+ Add task", lambda: self.task_dialog())

        toolbar = ttk.Frame(page, style="App.TFrame")
        toolbar.pack(fill="x", pady=(0, 14))
        ttk.Button(toolbar, text="‹", style="Quiet.TButton", command=lambda: self.change_month(-1)).pack(side="left")
        ttk.Button(toolbar, text="Today", style="Quiet.TButton", command=self.go_to_today).pack(side="left", padx=8)
        ttk.Button(toolbar, text="›", style="Quiet.TButton", command=lambda: self.change_month(1)).pack(side="left")
        ttk.Label(toolbar, text=month.strftime("%B %Y"), style="DialogTitle.TLabel").pack(side="right")

        grid = ttk.Frame(page, style="Card.TFrame", padding=1)
        grid.pack(fill="both", expand=True)
        for column in range(7):
            grid.columnconfigure(column, weight=1, uniform="calendar")
        for row in range(1, 7):
            grid.rowconfigure(row, weight=1, uniform="calendar")

        for column, label in enumerate(("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")):
            heading = tk.Label(grid, text=label, bg="#e8ede8", fg=MUTED, font=("DejaVu Sans", 9, "bold"), pady=8)
            heading.grid(row=0, column=column, sticky="nsew", padx=1, pady=1)

        tasks_by_day: dict[int, list[dict]] = {}
        for task in self.store.tasks(include_completed=True):
            due = task["due_date"]
            if due and due.year == month.year and due.month == month.month:
                tasks_by_day.setdefault(due.day, []).append(task)

        weeks = calendar.Calendar(firstweekday=calendar.MONDAY).monthdayscalendar(month.year, month.month)
        while len(weeks) < 6:
            weeks.append([0] * 7)
        today = date.today()
        for row, week in enumerate(weeks, 1):
            for column, day in enumerate(week):
                is_today = day and date(month.year, month.month, day) == today
                bg = "#edf6ef" if is_today else SURFACE
                cell = tk.Frame(grid, bg=bg, highlightbackground="#dfe5df", highlightthickness=1)
                cell.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                if not day:
                    continue
                number = tk.Label(cell, text=str(day), bg=bg, fg=GREEN if is_today else INK,
                                  font=("DejaVu Sans", 10, "bold" if is_today else "normal"))
                number.pack(anchor="ne", padx=7, pady=(5, 2))
                day_tasks = tasks_by_day.get(day, [])
                for task in day_tasks[:3]:
                    completed = task["completed"]
                    color = MUTED if completed else (RED if task["overdue"] else GREEN)
                    text = ("✓ " if completed else "• ") + task["name"]
                    event = tk.Label(cell, text=text, bg=bg, fg=color, anchor="w",
                                     font=("DejaVu Sans", 8), cursor="hand2")
                    event.pack(fill="x", padx=5, pady=1)
                    event.bind("<Button-1>", lambda _e, t=task: self.calendar_task_details(t))
                if len(day_tasks) > 3:
                    tk.Label(cell, text=f"+{len(day_tasks) - 3} more", bg=bg, fg=MUTED,
                             font=("DejaVu Sans", 8)).pack(anchor="w", padx=8, pady=1)

    def change_month(self, amount: int):
        year = self.calendar_month.year
        month = self.calendar_month.month + amount
        if month == 0:
            year, month = year - 1, 12
        elif month == 13:
            year, month = year + 1, 1
        self.calendar_month = date(year, month, 1)
        self.show_page("Calendar")

    def go_to_today(self):
        self.calendar_month = date.today().replace(day=1)
        self.show_page("Calendar")

    def calendar_task_details(self, task: dict):
        status = "Completed" if task["completed"] else ("Overdue" if task["overdue"] else "Open")
        messagebox.showinfo(task["name"], f"Due: {task['due_date']}\nRoom: {task['room'] or '—'}\nBatch: {task['batch'] or '—'}\nStatus: {status}")

    def task_dialog(self,task=None):
        rooms=self.store.rooms();batches=self.store.batches()
        if not rooms or not batches:messagebox.showinfo("Set up required","Add an active batch before creating tasks.");return
        rn=[r["name"] for r in rooms];bn=[b["name"] for b in batches]
        fields=[{"key":"name","label":"Task","value":task["name"] if task else ""},{"key":"due","label":"Due date (YYYY-MM-DD)","value":task["due_date"] if task else date.today()},
                {"key":"room","label":"Room","type":"choice","values":rn,"value":task["room"] if task else rn[0]},{"key":"batch","label":"Batch","type":"choice","values":bn,"value":task["batch"] if task else bn[0]}]
        def save(v):
            self._require(v["name"],"Task name")
            try:due=date.fromisoformat(v["due"])
            except ValueError:raise ValueError("Due date must use YYYY-MM-DD.")
            rid=next(r["id"] for r in rooms if r["name"]==v["room"]);bid=next(b["id"] for b in batches if b["name"]==v["batch"])
            self.store.save_task(v["name"],due,rid,bid,task["id"] if task else None);self.show_page("Tasks")
        FormDialog(self,"Edit task" if task else "Add task",fields,save)

    def task_complete(self,task):
        if not task:return
        try:self.store.complete_task(task["id"],not task["completed"]);self.show_page("Tasks")
        except DataError as exc:messagebox.showerror("Action failed",str(exc))

    def task_delete(self,task):
        if task:self.confirm_delete("task",lambda:(self.store.delete_task(task["id"]),self.show_page("Tasks")))

    def settings_page(self,page):
        self.header(page,"Facility settings","Defaults used to plan your cultivation cycle")
        facility=self.store.facility() or {}
        card=ttk.Frame(page,style="Card.TFrame",padding=28);card.pack(fill="x")
        inputs={}
        fields=[("name","Facility name"),("clone_days","Clone days"),("veg_days","Veg days"),("flower_days","Flower days"),("dry_days","Dry days")]
        for row,(key,label) in enumerate(fields):
            ttk.Label(card,text=label,style="Form.TLabel").grid(row=row,column=0,sticky="w",padx=(0,30),pady=9)
            entry=ttk.Entry(card,width=38);entry.grid(row=row,column=1,sticky="w",pady=9);entry.insert(0,str(facility.get(key,"")));inputs[key]=entry
        def save():
            try:
                name=inputs["name"].get().strip();self._require(name,"Facility name")
                values=[int(inputs[k].get()) for k in ("clone_days","veg_days","flower_days","dry_days")]
                if any(v<1 for v in values):raise ValueError("Phase lengths must be at least one day.")
                self.store.save_facility(name,*values);messagebox.showinfo("Saved","Facility settings updated.");self.show_page("Settings")
            except (ValueError,DataError) as exc:messagebox.showerror("Couldn't save",str(exc))
        ttk.Button(card,text="Save settings",style="Primary.TButton",command=save).grid(row=len(fields),column=1,sticky="w",pady=(18,0))

    @staticmethod
    def _require(value: str,label: str):
        if not value.strip():raise ValueError(f"{label} is required.")


def run() -> None:
    CultivationApp().mainloop()

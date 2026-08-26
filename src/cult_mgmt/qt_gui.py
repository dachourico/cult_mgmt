"""Modern Qt desktop interface for the Cultivation Management Suite."""

from __future__ import annotations

import sys
from datetime import date
from typing import Callable

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QApplication, QCalendarWidget, QCheckBox, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
    QPushButton, QScrollArea, QSpinBox, QStackedWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from cult_mgmt.app_data import CultivationStore, DataError


GREEN = "#2f7650"
INK = "#17231c"
MUTED = "#6c786f"
RED = "#bb454b"
BG = "#f4f7f3"

STYLESHEET = """
* { font-family: "Segoe UI", "Inter", sans-serif; font-size: 14px; color: #17231c; }
QMainWindow, QWidget#root { background: #f4f7f3; }
QFrame#sidebar { background: #132e20; border: none; }
QLabel#brand { color: white; font-size: 22px; font-weight: 700; letter-spacing: 1px; }
QLabel#brandSub { color: #99b4a2; font-size: 11px; letter-spacing: 1px; }
QPushButton[nav="true"] { color: #dce8df; background: transparent; border: none; border-radius: 10px; text-align: left; padding: 13px 17px; font-size: 14px; }
QPushButton[nav="true"]:hover { background: #1d432e; color: white; }
QPushButton[nav="true"][active="true"] { background: #2d6d49; color: white; font-weight: 600; }
QLabel#title { font-size: 30px; font-weight: 750; color: #152119; }
QLabel#subtitle { color: #6c786f; font-size: 13px; }
QFrame#card { background: white; border: 1px solid #e1e8e1; border-radius: 16px; }
QLabel#metricLabel { color: #758078; font-size: 11px; font-weight: 700; letter-spacing: 1px; }
QLabel#metricValue { font-size: 31px; font-weight: 750; }
QPushButton { background: #e8eee9; border: none; border-radius: 9px; padding: 10px 16px; font-weight: 600; }
QPushButton:hover { background: #dce6de; }
QPushButton[primary="true"] { background: #2f7650; color: white; }
QPushButton[primary="true"]:hover { background: #286745; }
QPushButton[danger="true"] { background: #f7e7e7; color: #a83940; }
QLineEdit, QComboBox, QSpinBox { background: white; border: 1px solid #d9e2da; border-radius: 8px; padding: 9px; min-height: 20px; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #4a9167; }
QTableWidget { background: white; border: 1px solid #e1e8e1; border-radius: 14px; gridline-color: #edf1ed; selection-background-color: #dfeee3; selection-color: #17231c; }
QHeaderView::section { background: #eef3ee; border: none; border-bottom: 1px solid #dfe6df; padding: 12px; color: #657168; font-size: 11px; font-weight: 700; }
QTableWidget::item { padding: 11px; border-bottom: 1px solid #edf1ed; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 3px; }
QScrollBar::handle:vertical { background: #c9d5cc; border-radius: 4px; min-height: 35px; }
QCalendarWidget { background: white; border: 1px solid #e1e8e1; border-radius: 14px; }
QCalendarWidget QToolButton { color: #17231c; background: transparent; font-size: 16px; padding: 8px; }
QCalendarWidget QAbstractItemView { selection-background-color: #2f7650; selection-color: white; outline: none; }
QListWidget { background: white; border: 1px solid #e1e8e1; border-radius: 14px; padding: 8px; }
QListWidget::item { padding: 12px; border-bottom: 1px solid #edf1ed; }
QDialog { background: #f7f9f7; }
QCheckBox { spacing: 8px; color: #556159; }
"""


class RecordTable(QTableWidget):
    def __init__(self, columns: list[str]):
        super().__init__(0, len(columns))
        self.records: list[dict] = []
        self.setHorizontalHeaderLabels(columns)
        self.verticalHeader().hide()
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setDefaultSectionSize(48)

    def set_records(self, records: list[dict], values: Callable[[dict], list]):
        self.records = records
        self.setRowCount(len(records))
        for row, record in enumerate(records):
            for column, value in enumerate(values(record)):
                item = QTableWidgetItem("—" if value is None else str(value))
                self.setItem(row, column, item)

    def selected_record(self) -> dict | None:
        row = self.currentRow()
        return self.records[row] if 0 <= row < len(self.records) else None


class DataDialog(QDialog):
    def __init__(self, parent, title: str, fields: list[dict], save: Callable[[dict], None]):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(440)
        self.save_callback = save
        self.inputs = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 25, 28, 25)
        heading = QLabel(title); heading.setObjectName("title"); heading.setStyleSheet("font-size: 22px;")
        layout.addWidget(heading)
        form = QFormLayout(); form.setSpacing(13); form.setContentsMargins(0, 15, 0, 12)
        for field in fields:
            if field.get("type") == "choice":
                widget = QComboBox(); widget.addItems(field["values"])
                widget.setCurrentText(str(field.get("value", "")))
            elif field.get("type") == "number":
                widget = QSpinBox(); widget.setRange(field.get("minimum", 1), 1_000_000)
                widget.setValue(int(field.get("value") or field.get("minimum", 1)))
            else:
                widget = QLineEdit(str(field.get("value") or ""))
                widget.setPlaceholderText(field.get("placeholder", ""))
            self.inputs[field["key"]] = widget
            form.addRow(field["label"], widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save)
        buttons.rejected.connect(self.reject); buttons.accepted.connect(self.try_save)
        buttons.button(QDialogButtonBox.StandardButton.Save).setProperty("primary", True)
        layout.addWidget(buttons)

    def try_save(self):
        values = {}
        for key, widget in self.inputs.items():
            values[key] = widget.value() if isinstance(widget, QSpinBox) else widget.currentText() if isinstance(widget, QComboBox) else widget.text().strip()
        try:
            self.save_callback(values)
        except (DataError, ValueError) as exc:
            QMessageBox.critical(self, "Couldn't save", str(exc)); return
        self.accept()


class CultivationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.store = CultivationStore()
        self.setWindowTitle("Cultivation Management Suite")
        self.resize(1320, 840)
        self.setMinimumSize(1080, 700)
        self.nav: dict[str, QPushButton] = {}
        self.current_page = "Dashboard"
        self._build()
        self.show_page("Dashboard")

    def _build(self):
        root = QWidget(); root.setObjectName("root"); self.setCentralWidget(root)
        row = QHBoxLayout(root); row.setContentsMargins(0, 0, 0, 0); row.setSpacing(0)
        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(225)
        side = QVBoxLayout(sidebar); side.setContentsMargins(17, 27, 17, 20); side.setSpacing(5)
        brand = QLabel("CULTIVATE"); brand.setObjectName("brand"); side.addWidget(brand)
        sub = QLabel("MANAGEMENT SUITE"); sub.setObjectName("brandSub"); side.addWidget(sub); side.addSpacing(25)
        for name, icon in [("Dashboard","⌂"),("Rooms","▦"),("Batches","●"),("Tasks","✓"),("Calendar","□"),("Strains","◇"),("Settings","⚙")]:
            button = QPushButton(f"{icon}    {name}"); button.setProperty("nav", True); button.setProperty("active", False)
            button.setCursor(Qt.CursorShape.PointingHandCursor); button.clicked.connect(lambda _=False, n=name: self.show_page(n))
            side.addWidget(button); self.nav[name] = button
        side.addStretch(); footer = QLabel("POSTGRESQL  •  QT DESKTOP"); footer.setObjectName("brandSub"); side.addWidget(footer)
        row.addWidget(sidebar)
        self.stack = QStackedWidget(); row.addWidget(self.stack, 1)

    def show_page(self, name: str):
        self.current_page = name
        for key, button in self.nav.items():
            button.setProperty("active", key == name); button.style().unpolish(button); button.style().polish(button)
        while self.stack.count():
            widget = self.stack.widget(0); self.stack.removeWidget(widget); widget.deleteLater()
        try:
            page = getattr(self, f"page_{name.lower()}")()
        except DataError as exc:
            page = self.error_page(exc)
        self.stack.addWidget(page)

    def page_shell(self, title: str, subtitle: str, action: tuple[str, Callable] | None = None) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(35, 28, 35, 30); layout.setSpacing(18)
        header = QHBoxLayout(); text = QVBoxLayout(); text.setSpacing(2)
        heading = QLabel(title); heading.setObjectName("title"); text.addWidget(heading)
        secondary = QLabel(subtitle); secondary.setObjectName("subtitle"); text.addWidget(secondary)
        header.addLayout(text); header.addStretch()
        if action:
            button = QPushButton(action[0]); button.setProperty("primary", True); button.clicked.connect(action[1]); header.addWidget(button)
        layout.addLayout(header)
        return page, layout

    def error_page(self, exc):
        page, layout = self.page_shell("Connection needed", "The app couldn't reach PostgreSQL")
        card = self.card(); box = QVBoxLayout(card); box.setContentsMargins(25,25,25,25)
        label=QLabel(str(exc)); label.setWordWrap(True); box.addWidget(label)
        retry=QPushButton("Try again");retry.setProperty("primary",True);retry.clicked.connect(lambda:self.show_page("Dashboard"));box.addWidget(retry,0,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(card);layout.addStretch();return page

    @staticmethod
    def card() -> QFrame:
        frame = QFrame(); frame.setObjectName("card"); return frame

    def page_dashboard(self):
        facility=self.store.facility(); stats=self.store.dashboard()
        page,layout=self.page_shell(facility["name"] if facility else "Your facility",date.today().strftime("Cultivation overview  •  %A, %B %d"))
        metrics=QHBoxLayout();metrics.setSpacing(13)
        for label,value in [("ACTIVE BATCHES",stats.get("active_batches",0)),("TOTAL PLANTS",stats.get("plants",0)),("ROOMS",stats.get("rooms",0)),("OPEN TASKS",stats.get("open_tasks",0))]:
            card=self.card();box=QVBoxLayout(card);box.setContentsMargins(20,17,20,17)
            a=QLabel(label);a.setObjectName("metricLabel");b=QLabel(str(value));b.setObjectName("metricValue");box.addWidget(a);box.addWidget(b);metrics.addWidget(card)
        layout.addLayout(metrics)
        content=QHBoxLayout();content.setSpacing(15)
        rooms_card=self.card();rb=QVBoxLayout(rooms_card);rb.setContentsMargins(22,20,22,20);rb.addWidget(self.section("ROOM STATUS"))
        rooms=self.store.rooms()
        if not rooms:rb.addWidget(QLabel("No rooms yet. Add your first room to begin."))
        for room in rooms:
            line=QHBoxLayout();dot=QLabel("●");dot.setStyleSheet(f"color: {GREEN};font-size:16px");line.addWidget(dot);line.addWidget(QLabel(f"<b>{room['name']}</b>"));phase=QLabel(room['room_type'].upper());phase.setObjectName("subtitle");line.addWidget(phase);line.addStretch();line.addWidget(QLabel(f"{room['plants']} plants"));rb.addLayout(line)
        rb.addStretch();content.addWidget(rooms_card,3)
        tasks_card=self.card();tb=QVBoxLayout(tasks_card);tb.setContentsMargins(22,20,22,20);tb.addWidget(self.section("NEXT UP"))
        tasks=self.store.tasks()[:7]
        if not tasks:tb.addWidget(QLabel("Nothing due. Nice work."))
        for task in tasks:
            label=QLabel(f"<b>{task['name']}</b><br><span style='color:{RED if task['overdue'] else MUTED}'>{task['room'] or '—'}  •  {task['due_date'] or 'No date'}</span>");tb.addWidget(label)
        tb.addStretch();content.addWidget(tasks_card,2);layout.addLayout(content,1);return page

    @staticmethod
    def section(text):
        label=QLabel(text);label.setObjectName("metricLabel");return label

    def page_rooms(self):
        page,layout=self.page_shell("Rooms","Capacity and current cultivation activity",("+  Add room",lambda:self.room_dialog()))
        table=RecordTable(["ROOM","PHASE","BATCHES","PLANTS"]);records=self.store.rooms();table.set_records(records,lambda r:[r['name'],r['room_type'].title(),r['batches'],r['plants']]);layout.addWidget(table,1)
        layout.addLayout(self.actions([("Edit",lambda:self.room_dialog(table.selected_record()),False),("Delete",lambda:self.remove("room",table.selected_record()),True)]));return page

    def room_dialog(self,record=None):
        if record is None and self.current_page!="Rooms":record=None
        dlg=DataDialog(self,"Edit room" if record else "Add room",[{"key":"name","label":"Room name","value":record['name'] if record else ""},{"key":"type","label":"Phase","type":"choice","values":["clone","veg","flower","dry"],"value":record['room_type'] if record else "clone"}],lambda v:(self.required(v['name'],"Room name"),self.store.save_room(v['name'],v['type'],record['id'] if record else None)))
        if dlg.exec():self.show_page("Rooms")

    def page_strains(self):
        page,layout=self.page_shell("Strains","Your reusable cultivar library",("+  Add strain",lambda:self.strain_dialog()))
        table=RecordTable(["STRAIN","ALL-TIME BATCHES","ACTIVE PLANTS"]);table.set_records(self.store.strains(),lambda r:[r['name'],r['batches'],r['plants']]);layout.addWidget(table,1)
        layout.addLayout(self.actions([("Rename",lambda:self.strain_dialog(table.selected_record()),False),("Delete",lambda:self.remove("strain",table.selected_record()),True)]));return page

    def strain_dialog(self,record=None):
        dlg=DataDialog(self,"Rename strain" if record else "Add strain",[{"key":"name","label":"Strain name","value":record['name'] if record else ""}],lambda v:(self.required(v['name'],"Strain name"),self.store.save_strain(v['name'],record['id'] if record else None)))
        if dlg.exec():self.show_page("Strains")

    def page_batches(self):
        page,layout=self.page_shell("Batches","Track plants from clone through harvest",("+  Add batch",lambda:self.batch_dialog()))
        show=QCheckBox("Show completed");layout.addWidget(show,0,Qt.AlignmentFlag.AlignRight)
        table=RecordTable(["BATCH","STRAIN","ROOM","PHASE","PLANTS","DAY","STATUS"]);layout.addWidget(table,1)
        def fill():table.set_records(self.store.batches(show.isChecked()),lambda r:[r['name'],r['strain'],r['room'],(r['phase'] or '—').title(),r['plant_count'],r['phase_day'],r['status'].title()])
        show.toggled.connect(fill);fill()
        layout.addLayout(self.actions([("Edit",lambda:self.batch_dialog(table.selected_record()),False),("Move",lambda:self.move_dialog(table.selected_record()),False),("Harvest",lambda:self.batch_action(table.selected_record(),"harvest"),False),("Finish",lambda:self.batch_action(table.selected_record(),"finish"),False),("Delete",lambda:self.batch_action(table.selected_record(),"delete"),True)]));return page

    def batch_dialog(self,record=None):
        rooms=self.store.rooms();strains=self.store.strains()
        if not rooms or not strains:QMessageBox.information(self,"Set up required","Add at least one room and strain first.");return
        fields=[{"key":"name","label":"Batch name","value":record['name'] if record else ""},{"key":"strain","label":"Strain","type":"choice","values":[s['name'] for s in strains],"value":record['strain'] if record else strains[0]['name']},{"key":"room","label":"Room","type":"choice","values":[r['name'] for r in rooms],"value":record['room'] if record else rooms[0]['name']},{"key":"count","label":"Plant count","type":"number","value":record['plant_count'] if record else 1}]
        def save(v):self.required(v['name'],"Batch name");self.store.save_batch(v['name'],next(s['id'] for s in strains if s['name']==v['strain']),next(r['id'] for r in rooms if r['name']==v['room']),v['count'],record['id'] if record else None)
        if DataDialog(self,"Edit batch" if record else "Add batch",fields,save).exec():self.show_page("Batches")

    def move_dialog(self,record):
        if not record:return
        rooms=self.store.rooms();dlg=DataDialog(self,f"Move {record['name']}",[{"key":"room","label":"Destination","type":"choice","values":[r['name'] for r in rooms],"value":record['room']}],lambda v:self.store.move_batch(record['id'],next(r['id'] for r in rooms if r['name']==v['room'])))
        if dlg.exec():self.show_page("Batches")

    def batch_action(self,record,action):
        if not record:return
        labels={"harvest":"Move this batch to dry and record today's harvest?","finish":"Mark this batch completed?","delete":"Permanently delete this batch?"}
        if QMessageBox.question(self,action.title(),labels[action])!=QMessageBox.StandardButton.Yes:return
        try:{"harvest":self.store.harvest_batch,"finish":self.store.finish_batch,"delete":self.store.delete_batch}[action](record['id']);self.show_page("Batches")
        except DataError as exc:QMessageBox.critical(self,"Action failed",str(exc))

    def page_tasks(self):
        page,layout=self.page_shell("Tasks","Work due across every room and batch",("+  Add task",lambda:self.task_dialog()))
        show=QCheckBox("Show completed");layout.addWidget(show,0,Qt.AlignmentFlag.AlignRight)
        table=RecordTable(["TASK","DUE","ROOM","BATCH","STATUS"]);layout.addWidget(table,1)
        def fill():table.set_records(self.store.tasks(show.isChecked()),lambda r:[r['name'],r['due_date'],r['room'],r['batch'],"Complete" if r['completed'] else "Overdue" if r['overdue'] else "Open"])
        show.toggled.connect(fill);fill()
        layout.addLayout(self.actions([("Edit",lambda:self.task_dialog(table.selected_record()),False),("Mark complete",lambda:self.task_complete(table.selected_record()),False),("Delete",lambda:self.remove("task",table.selected_record()),True)]));return page

    def task_dialog(self,record=None):
        rooms=self.store.rooms();batches=self.store.batches()
        if not rooms or not batches:QMessageBox.information(self,"Set up required","Add an active batch first.");return
        fields=[{"key":"name","label":"Task","value":record['name'] if record else ""},{"key":"due","label":"Due date (YYYY-MM-DD)","value":record['due_date'] if record else date.today()},{"key":"room","label":"Room","type":"choice","values":[r['name'] for r in rooms],"value":record['room'] if record else rooms[0]['name']},{"key":"batch","label":"Batch","type":"choice","values":[b['name'] for b in batches],"value":record['batch'] if record else batches[0]['name']}]
        def save(v):
            self.required(v['name'],"Task");due=date.fromisoformat(v['due']);self.store.save_task(v['name'],due,next(r['id'] for r in rooms if r['name']==v['room']),next(b['id'] for b in batches if b['name']==v['batch']),record['id'] if record else None)
        if DataDialog(self,"Edit task" if record else "Add task",fields,save).exec():self.show_page(self.current_page)

    def task_complete(self,record):
        if record:self.store.complete_task(record['id'],not record['completed']);self.show_page("Tasks")

    def page_calendar(self):
        page,layout=self.page_shell("Calendar","A visual schedule of cultivation work",("+  Add task",lambda:self.task_dialog()))
        split=QHBoxLayout();calendar_widget=QCalendarWidget();calendar_widget.setGridVisible(False);calendar_widget.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        tasks=self.store.tasks(True);event_dates={t['due_date'] for t in tasks if t['due_date']}
        fmt=QTextCharFormat();fmt.setBackground(QColor("#d9ede0"));fmt.setForeground(QColor(GREEN));fmt.setFontWeight(QFont.Weight.Bold)
        for day in event_dates:calendar_widget.setDateTextFormat(QDate(day.year,day.month,day.day),fmt)
        events=QListWidget();events.setMinimumWidth(330)
        def show_day(qdate):
            events.clear();chosen=date(qdate.year(),qdate.month(),qdate.day())
            for task in [t for t in tasks if t['due_date']==chosen]:
                status="✓ Complete" if task['completed'] else "! Overdue" if task['overdue'] else "• Open"
                item=QListWidgetItem(f"{task['name']}\n{task['room'] or '—'}  •  {task['batch'] or '—'}  •  {status}");item.setForeground(QColor(MUTED if task['completed'] else RED if task['overdue'] else GREEN));events.addItem(item)
            if not events.count():events.addItem("No work scheduled for this day.")
        calendar_widget.selectionChanged.connect(lambda:show_day(calendar_widget.selectedDate()));show_day(calendar_widget.selectedDate())
        split.addWidget(calendar_widget,3);split.addWidget(events,2);layout.addLayout(split,1);return page

    def page_settings(self):
        facility=self.store.facility() or {};page,layout=self.page_shell("Facility settings","Defaults used to plan your cultivation cycle")
        card=self.card();form=QFormLayout(card);form.setContentsMargins(28,28,28,28);form.setSpacing(14);inputs={}
        for key,label in [("name","Facility name"),("clone_days","Clone days"),("veg_days","Veg days"),("flower_days","Flower days"),("dry_days","Dry days")]:
            if key=="name":widget=QLineEdit(str(facility.get(key,"")))
            else:widget=QSpinBox();widget.setRange(1,365);widget.setValue(int(facility.get(key) or 1))
            inputs[key]=widget;form.addRow(label,widget)
        save=QPushButton("Save settings");save.setProperty("primary",True)
        def persist():
            try:self.required(inputs['name'].text(),"Facility name");self.store.save_facility(inputs['name'].text().strip(),*[inputs[k].value() for k in ('clone_days','veg_days','flower_days','dry_days')]);QMessageBox.information(self,"Saved","Facility settings updated.")
            except (DataError,ValueError) as exc:QMessageBox.critical(self,"Couldn't save",str(exc))
        save.clicked.connect(persist);form.addRow("",save);layout.addWidget(card);layout.addStretch();return page

    def actions(self,items):
        row=QHBoxLayout()
        for label,callback,danger in items:
            button=QPushButton(label);button.setProperty("danger",danger);button.clicked.connect(callback);row.addWidget(button)
        row.addStretch();return row

    def remove(self,noun,record):
        if not record:return
        if QMessageBox.question(self,f"Delete {noun}?",f"Permanently delete this {noun}?")!=QMessageBox.StandardButton.Yes:return
        try:getattr(self.store,f"delete_{noun}")(record['id']);self.show_page(self.current_page)
        except DataError as exc:QMessageBox.critical(self,"Couldn't delete",str(exc))

    @staticmethod
    def required(value,label):
        if not str(value).strip():raise ValueError(f"{label} is required.")


def run() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Cultivation Management Suite")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    window = CultivationWindow(); window.show()
    sys.exit(app.exec())

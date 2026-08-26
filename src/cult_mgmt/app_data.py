"""Database operations used by the desktop application.

The original repository modules keep a connection open at import time.  A GUI can
sit open all day, so this layer deliberately opens short-lived connections for
each action and returns dictionaries that are easy for the views to consume.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date
import os
from pathlib import Path
from typing import Any, Iterator

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")


class DataError(RuntimeError):
    """A database error safe to show in the interface."""


class CultivationStore:
    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        if not DATABASE_URL:
            raise DataError("DATABASE_URL is missing. Add it to your .env file.")
        try:
            with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
                yield conn
        except DataError:
            raise
        except psycopg.Error as exc:
            detail = getattr(exc.diag, "message_primary", None) or str(exc)
            raise DataError(detail or "Could not connect to PostgreSQL.") from exc

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict]:
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute(query, params)
            return list(cur.fetchall())

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict | None:
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        try:
            with self.connection() as conn, conn.cursor() as cur:
                cur.execute(query, params)
        except DataError as exc:
            if "duplicate key" in str(exc).lower():
                raise DataError("That name is already in use.") from exc
            if "foreign key" in str(exc).lower():
                raise DataError("This record is still in use and cannot be deleted.") from exc
            raise

    # Facility
    def facility(self) -> dict | None:
        return self.fetch_one(
            "SELECT id, name, clone_days, veg_days, flower_days, dry_days "
            "FROM facilities ORDER BY id LIMIT 1"
        )

    def save_facility(self, name: str, clone: int, veg: int, flower: int, dry: int) -> None:
        current = self.facility()
        if current:
            self.execute(
                "UPDATE facilities SET name=%s, clone_days=%s, veg_days=%s, "
                "flower_days=%s, dry_days=%s WHERE id=%s",
                (name, clone, veg, flower, dry, current["id"]),
            )
        else:
            self.execute(
                "INSERT INTO facilities (name, clone_days, veg_days, flower_days, dry_days) "
                "VALUES (%s,%s,%s,%s,%s)",
                (name, clone, veg, flower, dry),
            )

    # Rooms
    def rooms(self) -> list[dict]:
        return self.fetch_all(
            """SELECT r.id, r.name, r.room_type,
                      COUNT(pb.id) FILTER (WHERE pb.status = 'active') AS batches,
                      COALESCE(SUM(pb.plant_count) FILTER (WHERE pb.status = 'active'), 0) AS plants
               FROM rooms r
               LEFT JOIN plant_batches pb ON pb.current_room_id = r.id
               GROUP BY r.id, r.name, r.room_type
               ORDER BY CASE r.room_type WHEN 'clone' THEN 1 WHEN 'veg' THEN 2
                         WHEN 'flower' THEN 3 WHEN 'dry' THEN 4 ELSE 5 END, r.name"""
        )

    def save_room(self, name: str, room_type: str, room_id: int | None = None) -> None:
        if room_type not in {"clone", "veg", "flower", "dry"}:
            raise DataError("Room type must be clone, veg, flower, or dry.")
        facility = self.facility()
        if not facility:
            raise DataError("Create your facility before adding rooms.")
        if room_id:
            self.execute("UPDATE rooms SET name=%s, room_type=%s WHERE id=%s", (name, room_type, room_id))
        else:
            self.execute(
                "INSERT INTO rooms (name, room_type, facility_id) VALUES (%s,%s,%s)",
                (name, room_type, facility["id"]),
            )

    def delete_room(self, room_id: int) -> None:
        self.execute("DELETE FROM rooms WHERE id=%s", (room_id,))

    # Strains
    def strains(self) -> list[dict]:
        return self.fetch_all(
            """SELECT s.id, s.name, COUNT(pb.id) AS batches,
                      COALESCE(SUM(pb.plant_count) FILTER (WHERE pb.status='active'), 0) AS plants
               FROM strains s LEFT JOIN plant_batches pb ON pb.strain_id=s.id
               GROUP BY s.id, s.name ORDER BY LOWER(s.name)"""
        )

    def save_strain(self, name: str, strain_id: int | None = None) -> None:
        if strain_id:
            self.execute("UPDATE strains SET name=%s WHERE id=%s", (name, strain_id))
        else:
            self.execute("INSERT INTO strains (name) VALUES (%s)", (name,))

    def delete_strain(self, strain_id: int) -> None:
        self.execute("DELETE FROM strains WHERE id=%s", (strain_id,))

    # Batches
    def batches(self, include_finished: bool = False) -> list[dict]:
        where = "" if include_finished else "WHERE pb.status='active'"
        return self.fetch_all(
            f"""SELECT pb.id, pb.name, s.name AS strain, r.name AS room,
                       r.room_type AS phase, pb.plant_count, pb.status,
                       pb.initialized_date, pb.phase_start_date, pb.harvest_date,
                       CURRENT_DATE - pb.phase_start_date + 1 AS phase_day
                FROM plant_batches pb
                LEFT JOIN strains s ON s.id=pb.strain_id
                LEFT JOIN rooms r ON r.id=pb.current_room_id
                {where}
                ORDER BY CASE pb.status WHEN 'active' THEN 1 ELSE 2 END,
                         pb.phase_start_date, LOWER(pb.name)"""
        )

    def save_batch(
        self, name: str, strain_id: int, room_id: int, plant_count: int,
        batch_id: int | None = None,
    ) -> None:
        if plant_count < 1:
            raise DataError("Plant count must be at least 1.")
        if batch_id:
            self.execute(
                "UPDATE plant_batches SET name=%s, strain_id=%s, current_room_id=%s, plant_count=%s WHERE id=%s",
                (name, strain_id, room_id, plant_count, batch_id),
            )
        else:
            self.execute(
                """INSERT INTO plant_batches
                   (name, strain_id, current_room_id, plant_count, initialized_date, phase_start_date, status)
                   VALUES (%s,%s,%s,%s,CURRENT_DATE,CURRENT_DATE,'active')""",
                (name, strain_id, room_id, plant_count),
            )

    def move_batch(self, batch_id: int, room_id: int) -> None:
        self.execute(
            "UPDATE plant_batches SET current_room_id=%s, phase_start_date=CURRENT_DATE WHERE id=%s",
            (room_id, batch_id),
        )

    def harvest_batch(self, batch_id: int) -> None:
        dry = self.fetch_one("SELECT id FROM rooms WHERE room_type='dry' ORDER BY id LIMIT 1")
        if not dry:
            raise DataError("Add a dry room before harvesting a batch.")
        self.execute(
            "UPDATE plant_batches SET current_room_id=%s, phase_start_date=CURRENT_DATE, harvest_date=CURRENT_DATE WHERE id=%s",
            (dry["id"], batch_id),
        )

    def finish_batch(self, batch_id: int) -> None:
        self.execute("UPDATE plant_batches SET status='completed' WHERE id=%s", (batch_id,))

    def delete_batch(self, batch_id: int) -> None:
        self.execute("DELETE FROM plant_batches WHERE id=%s", (batch_id,))

    # Tasks
    def tasks(self, include_completed: bool = False) -> list[dict]:
        where = "" if include_completed else "WHERE t.completed=FALSE"
        return self.fetch_all(
            f"""SELECT t.id, t.name, t.due_date, t.completed, t.completed_date,
                       r.name AS room, pb.name AS batch, t.room_id, t.batch_id,
                       CASE WHEN NOT t.completed AND t.due_date < CURRENT_DATE THEN TRUE ELSE FALSE END AS overdue
                FROM tasks t
                LEFT JOIN rooms r ON r.id=t.room_id
                LEFT JOIN plant_batches pb ON pb.id=t.batch_id
                {where}
                ORDER BY t.completed, t.due_date NULLS LAST, LOWER(t.name)"""
        )

    def save_task(
        self, name: str, due_date: date, room_id: int, batch_id: int,
        task_id: int | None = None,
    ) -> None:
        if task_id:
            self.execute(
                "UPDATE tasks SET name=%s, due_date=%s, room_id=%s, batch_id=%s WHERE id=%s",
                (name, due_date, room_id, batch_id, task_id),
            )
        else:
            self.execute(
                "INSERT INTO tasks (name,due_date,room_id,batch_id,completed) VALUES (%s,%s,%s,%s,FALSE)",
                (name, due_date, room_id, batch_id),
            )

    def complete_task(self, task_id: int, completed: bool = True) -> None:
        self.execute(
            "UPDATE tasks SET completed=%s, completed_date=%s WHERE id=%s",
            (completed, date.today() if completed else None, task_id),
        )

    def delete_task(self, task_id: int) -> None:
        self.execute("DELETE FROM tasks WHERE id=%s", (task_id,))

    def dashboard(self) -> dict:
        return self.fetch_one(
            """SELECT
                 (SELECT COUNT(*) FROM plant_batches WHERE status='active') AS active_batches,
                 (SELECT COALESCE(SUM(plant_count),0) FROM plant_batches WHERE status='active') AS plants,
                 (SELECT COUNT(*) FROM rooms) AS rooms,
                 (SELECT COUNT(*) FROM tasks WHERE completed=FALSE) AS open_tasks,
                 (SELECT COUNT(*) FROM tasks WHERE completed=FALSE AND due_date<CURRENT_DATE) AS overdue"""
        ) or {}

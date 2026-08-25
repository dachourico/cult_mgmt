from db.connection import get_connection
from repositories.room_repository import get_room_id
from repositories.batch_repository import get_batch_id
from datetime import date

conn = get_connection()

def create_task(room, batch, task_name, due_date):
    room_id = get_room_id(room)
    batch_id = get_batch_id(batch)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO tasks
                (batch_id, room_id, name, due_date, completed)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                batch_id,
                room_id,
                task_name,
                due_date,
                False
            )
        )

    conn.commit()

def edit_task(room, batch, old_task, new_task):
    room_id = get_room_id(room)
    batch_id = get_batch_id(batch)

    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE tasks
            SET name = %s
            WHERE name = %s AND room_id = %s AND batch_id = %s
            """,
            (
                new_task,
                old_task,
                room_id,
                batch_id
            )
        )
    conn.commit()

def view_tasks_by_room(room):
    room_id = get_room_id(room)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT name
            FROM tasks
            WHERE room_id = %s AND completed = FALSE
            """,
            (
                room_id,
            )
        )
        tasks = cur.fetchall()
    return tasks

def view_tasks_by_batch(batch):
    batch_id = get_batch_id(batch)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT name
            FROM tasks
            WHERE batch_id = %s AND completed = FALSE
            """,
            (
                batch_id,
            )
        )
        tasks = cur.fetchall()
    return tasks

def delete_tasks(room, batch, task):
    room_id = get_room_id(room)
    batch_id = get_batch_id(batch)
    
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM tasks
            WHERE name = %s AND room_id = %s AND batch_id = %s
            """,
            (
                task,
                room_id,
                batch_id
            )
        )
    conn.commit()

def task_completed(room, batch, task):
    room_id = get_room_id(room)
    batch_id = get_batch_id(batch)
    completed_date = date.today()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE tasks
            SET completed = %s, completed_date = %s
            WHERE name = %s AND room_id = %s AND batch_id = %s
            """,
            (
                'true',
                completed_date,
                task,
                room_id,
                batch_id
            )
        )
    conn.commit()
from repositories.room_repository import view_rooms, get_room_id, get_dry_room
from repositories.facility_repository import get_facility
from db.connection import get_connection
from repositories.strain_repository import get_strain_id
from datetime import date

conn = get_connection()

def get_batch_id(batch_name):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM plant_batches
            WHERE name = %s
            """,
            (
                batch_name,
            )
        )
        fetch_batch_id = cur.fetchone()
        if fetch_batch_id is None:
            return None
        batch_id = fetch_batch_id[0]
    return batch_id

def create_batch(name, strain, room, plant_count):
    init_date = date.today()
    phase_start_date = date.today()
    strain_id = get_strain_id(strain)
    room_id = get_room_id(room)
    status = "active"

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO plant_batches (name, strain_id, current_room_id, plant_count, initialized_date, phase_start_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                name,
                strain_id,
                room_id,
                plant_count,
                init_date,
                phase_start_date,
                status
            )
        )
        conn.commit()

def edit_batch_name(old_name, new_name):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE plant_batches
            SET name = %s
            WHERE name = %s
            """,
            (
                new_name,
                old_name
            )
        )
        conn.commit()

def edit_batch_strain(batch_name, new_strain):
    batch_id = get_batch_id(batch_name)
    new_strain_id = get_strain_id(new_strain)

    if batch_id is None:
        return "Batch doesn't exist"
    elif new_strain_id is None:
        return "Strain doesn't exist"
    
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE plant_batches
            SET strain_id = %s
            WHERE id = %s
            """,
            (
                new_strain_id,
                batch_id
            )
        )
        conn.commit()

def edit_plant_count(batch_name, new_count):
    batch_id = get_batch_id(batch_name)
    if batch_id is None:
        return "Batch doesn't exist"
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE plant_batches
            SET plant_count = %s
            WHERE id = %s
            """,
            (
                new_count,
                batch_id
            )
        )
    conn.commit()

def delete_batch(batch_name):
    batch_id = get_batch_id(batch_name)
    if batch_id is None:
        return "Batch doesn't exist"

    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM plant_batches
            WHERE id = %s
            """,
            (
                batch_id,
            )
        )
    conn.commit()

def view_active_batches():
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT name
            FROM plant_batches
            WHERE status = 'active'
            """
        )

        active_batches = cur.fetchall()
        
    return active_batches   

def view_batches_by_room(room):
    room_id = get_room_id(room)
    if room_id is None:
        return "Room doesn't exist"
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT name
            FROM plant_batches
            WHERE current_room_id = %s
            """,
            (
                room_id,
            )
        )
        batches = cur.fetchall()
    return batches

def move_batch(batch_name, new_room):

    batch_id = get_batch_id(batch_name)
    if batch_id is None:
        return "Batch doesn't exist"
    
    room_id = get_room_id(new_room)
    if room_id is None:
        return "Room doesn't exist"
    
    new_phase = date.today()
    
    
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE plant_batches
            SET current_room_id = %s
            WHERE id = %s
            """,
            (
                room_id,
                batch_id
            )
        )
        cur.execute(
            """
            UPDATE plant_batches
            SET phase_start_date = %s
            WHERE id = %s
            """,
            (
                new_phase,
                batch_id
            )
        )
    conn.commit()

def harvest_batch(batch_name):
    batch_id = get_batch_id(batch_name)
    if batch_id is None:
        return "Batch doesn't exist"
    current_date = date.today()
    dry_room = get_dry_room()
    if dry_room is None:
        return "No dry room exists."
    
    result = move_batch(batch_name, dry_room)
    if result:
        return result
    
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE plant_batches
            SET harvest_date = %s
            WHERE id = %s
            """,
            (
                current_date,
                batch_id
            )
        )
    conn.commit()

def get_day_count(batch_name):
    current_date = date.today()
    batch_id = get_batch_id(batch_name)
    if batch_id is None:
        return None
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT phase_start_date
            FROM plant_batches
            WHERE id = %s
            """,
            (
                batch_id,
            )
        )
        fetch_start_date = cur.fetchone()
        if fetch_start_date is None:
            return None
        start_date = fetch_start_date[0]
        
    day_count = (current_date - start_date).days + 1
    return day_count

def get_batch_info(batch_name):
    batch_id = get_batch_id(batch_name)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM plant_batches
            WHERE id = %s
            """,
            (
                batch_id,
            )
        )
        batch_info = cur.fetchone()
    return batch_info
    
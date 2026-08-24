from db.connection import get_connection
from facility_repository import get_facility



conn = get_connection()



def create_room(room_name, room_type):
    facility = get_facility()
    facility_id = facility[0]

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO rooms (name, room_type, facility_id)
            VALUES (%s, %s, %s)
            """,
            (
                room_name,
                room_type,
                facility_id
            )
        )
    conn.commit()

def view_rooms():
    facility = get_facility()
    facility_id = facility[0]
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT name
            FROM rooms
            WHERE facility_id = %s
            """,
            (facility_id,)
        )
        rooms = cur.fetchall()

    return rooms

    
    

def edit_room_name(room, new_name):
    facility = get_facility()
    facility_id = facility[0]
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE rooms
            SET name = %s
            WHERE name = %s AND facility_id = %s
            """,
            (
                new_name,
                room,
                facility_id
            )
        )
    conn.commit()

def edit_room_type(room, new_type):
    facility = get_facility()
    facility_id = facility[0]
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE rooms
            SET room_type = %s
            WHERE name = %s AND facility_id = %s
            """,
            (
                new_type,
                room,
                facility_id
            )
        )

def delete_rooms(name):
    warning = str(input(f"Are you sure you want to delete {name}?"))
    facility = get_facility()
    facility_id = facility[0]

    if warning.lower() == "yes":
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM rooms
                WHERE name = %s AND facility_id = %s
                """,
                (
                    name,
                    facility_id
                )
            )
        conn.commit()

    

def get_room_id(room):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM rooms
            WHERE room = %s
            """,
            (room,)
        )
        fetch_room_id = cur.fetchone()
        if fetch_room_id is None:
            return None
        room_id = fetch_room_id[0]

    return room_id


def get_dry_room():
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT name
            FROM rooms
            WHERE room_type = 'dry'
            """
        )

        fetch_dry_room = cur.fetchone()
        if fetch_dry_room is None:
            return None
        dry_room = fetch_dry_room[0]

    return dry_room

def get_room_content(room):
    room_id = get_room_id(room)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
            r.name AS room_name,
            r.room_type,
            pb.name AS batch_name,
            s.name AS strain_name,
            pb.plant_count
            FROM rooms r
            LEFT JOIN plant_batches pb
                ON pb.current_room_id = r.id
            LEFT JOIN strains s
                ON pb.strain_id = s.id
            WHERE r.id = %s;
            """,
            (
                room_id,
            )
        )

        room_content = cur.fetchall()

    return room_content






    
    
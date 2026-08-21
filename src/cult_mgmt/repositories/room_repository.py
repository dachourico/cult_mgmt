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

    

    
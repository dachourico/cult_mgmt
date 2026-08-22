from db.connection import get_connection
from facility_repository import get_facility

conn = get_connection()

def create_strain(name):
    facility = get_facility()
    facility_id = facility[0]

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO strains (name)
            VALUES (%s)
            """,
            (
                name,
            )
        )
    conn.commit()

def view_strains():
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT name
            FROM strains
            """
        )
        strains = cur.fetchall()

    return strains

def edit_strains(old_name, new_name):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE strains
            SET name = %s
            WHERE name = %s
            """,
            (
                new_name,
                old_name
            )
        )
    conn.commit()

def delete_strains():
    pass
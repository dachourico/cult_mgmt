from db.connection import get_connection
from facility_repository import get_facility
import psycopg

conn = get_connection()

def create_strain(name):

    try:
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

    except psycopg.errors.UniqueViolation:
        conn.rollback()
        return f"Sorry {name} already exists."

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

    try:
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
    except psycopg.errors.UniqueViolation:
        conn.rollback()
        return f"Sorry {new_name} already exists."

def delete_strains(name):
    warning = input(f"Are you sure you want to delete {name}? ")

    if warning.lower() == "yes":
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM strains
                WHERE name = %s
                """,
                (
                    name,
                )
            )
        conn.commit()

def get_strain_id(strain):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM strains
            WHERE name = %s
            """,
            (
                strain,
            )
        )
        fetch_strain_id = cur.fetchone()
        strain_id = fetch_strain_id[0]
    return strain_id

    

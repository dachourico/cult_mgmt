from db.connection import get_connection


conn = get_connection()

def get_facility():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, clone_days, veg_days, flower_days, dry_days
            FROM facilities
            LIMIT 1;
        """)

        return cur.fetchone()
    
facility = get_facility()


def edit_facility_name(facility_id, new_name):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE facilities
            SET name = %s
            WHERE id = %s
            """,
            (
                new_name,
                facility_id
            )
        )
    conn.commit()
    

def update_clone_days(facility_id, new_clone):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE facilities
            SET clone_days = %s
            WHERE id = %s
            """,
            (
                new_clone,
                facility_id
            )
        )
    conn.commit()

def update_veg_days(facility_id, new_veg):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE facilities
            SET veg_days = %s
            WHERE id = %s
            """,
            (
                new_veg,
                facility_id
            )
        )
    conn.commit()

def update_flower_days(facility_id, new_flower):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE facilities
            SET flower_days = %s
            WHERE id = %s
            """,
            (
                new_flower,
                facility_id
            )
        )
    conn.commit()

def update_dry_days(facility_id, new_dry):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE facilities
            SET dry_days = %s
            WHERE id = %s
            """,
            (
                new_dry,
                facility_id
            )
        )
    conn.commit()



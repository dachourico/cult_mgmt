from db.connection import get_connection

conn = get_connection()

def get_facility(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, clone_days, veg_days, flower_days, dry_days
            FROM facilities
            LIMIT 1;
        """)

        return cur.fetchone()

facility = get_facility(conn)

def first_use():
    print("Welcome to your Cultivation Management Suite!")
    facility_name = input("What is your facility name? ")
    clone_days = int(input("How long in clone? "))
    veg_days = int(input("How long in veg? "))
    flower_days = int(input("How long in flower? "))

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO facilities
                (name, clone_days, veg_days, flower_days, dry_days) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                facility_name,
                clone_days,
                veg_days,
                flower_days,
                dry_days
            )
        )
    
    conn.commit()





def main():

    if facility is None:
        first_use()


main()

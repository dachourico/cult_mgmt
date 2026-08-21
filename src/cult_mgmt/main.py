from db.connection import get_connection
from repositories.facility_repository import *






def first_use():
    print("Welcome to your Cultivation Management Suite!")
    facility_name = input("What is your facility name? ")
    clone_days = int(input("How long in clone? "))
    veg_days = int(input("How long in veg? "))
    flower_days = int(input("How long in flower? "))
    dry_days = int(input("How long in dry? "))

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
    print(f"Welcome back to {home_facility}!")
    

    

main()

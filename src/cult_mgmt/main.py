from db.connection import get_connection
from repositories.facility_repository import *
from repositories.room_repository import *
from repositories.batch_repository import *
from repositories.strain_repository import *
from repositories.task_repository import *
from services.scheduling import *






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

def main_menu():
    while True:
        choice = input(f"""Type the number to navigate\n
        1. Room stuff\n
        2. Plant batch stuff\n
        3. Strain stuff\n
        4. Task stuff\n
        5. Exit
        """)

        if choice == "1":
            room_menu()

        elif choice == "2":
            batch_menu()

        elif choice == "3":
            strain_menu()

        elif choice == "4":
            task_menu()

        elif choice == "5":
            print("See you later!")
            return

        else:
            return "You know I don't speak Taco Bell, try a number 1-5."

def room_menu():

    while True:
        choice = input("""
        What brings you in today?\n
        1. Create room\n
        2. Edit room name or type\n
        3. View list of rooms
        4. View room contents\n
        5. Delete room
        6. Back to main menu
        """)

        if choice == "1":
            room_name = input("What is the name of the room you want to create? ")
            room_type = input("Is it a clone, veg, flower, or dry room? ")
            try:
                create_room(room_name, room_type)
                print(f"Room {room_name} created!")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            room_or_type = input("Would you like to change the room name or type? Enter 'room' or 'type' ")
            if room_or_type == "room":
                room = input("What room are we changing? ")
                new_name = input("What would you like to change the name to? ")
                try:
                    edit_room_name(room, new_name)
                    print(f"Room {room} is now {new_name}!")
                except Exception as e:
                    print(f"Error: {e}")
            elif room_or_type == "type":
                room = input("What room are we changing? ")
                new_type = input("What would you like to change the type to? ")
                try:
                    edit_room_type(room, new_type)
                    print(f"Room {room} is now a {new_type} room!")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Try again, only 'room' or 'type' are acceptable here.")

        elif choice == "3":
            try:
                print(f"Here are those rooms you ordered: {view_rooms()}")
            except Exception as e:
                print(f"Error:{e}")

        elif choice == "4":
            room = input("What room would you like to see? ")
            try:
                print(f"Here are those contents you ordered: {get_room_content(room)}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "5":
            room = input("What room are we sending to the dark abyss today? ")
            try:
                delete_rooms(room)
                print(f"Your bidding is done. {room} is no more, Sire.")
            except Exception as e:
                print(f"Error: {e}")


        elif choice == "6":
            return

        else:
            print("Invalid choice hombre, try typing a number between 1 and 6")

def batch_menu():
    while True:
        choice = input("""
        What brings you in today?\n
        1. View active batches by room\n
        2. Create batches\n
        3. Edit batch\n
        4. Move batch\n
        5. Delete batch\n
        6. Harvest batch\n
        7. Back to main menu
        """)

        if choice == "1":
            room = input("What room do you want to look at? ")
            try:
    
                print(f"Here are all of the active batches in {room}: {view_batches_by_room(room)}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            
            try:
                name = input("What do you want to name this batch? ")
                strain = input("What strain is it? ")
                room = input("Where is it going? ")
                plant_count = int(input("How many of these bad Larrys are there? "))
                create_batch(name, strain, room, plant_count)
                print(f"Batch {name} was successfully created and put into {room}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            edit_choice = input("Would you like to edit name, strain, or plant count? ")

            if edit_choice == "name":
                old_name = input("What batch are you trying to change? ")
                new_name = input("What would you like to change the name to? ")
                try:
                    edit_batch_name(old_name, new_name)
                    print(f"{old_name} is now {new_name}")
                except Exception as e:
                    print(f"Error: {e}")

            elif edit_choice == "strain":
                batch_name = input("What batch are you trying to change? ")
                new_strain = input("What is the updated strain name? ")
                try:
                    edit_batch_strain(batch_name, new_strain)
                    print(f"{batch_name}'s strain has been updated to {new_strain}")
                except Exception as e:
                    print(f"Error: {e}")

            elif edit_choice == "plant count":
                try:
                    batch_name = input("What batch are you trying to change? ")
                    new_count = int(input("What is the updated plant count? (Must be a number) "))
                    edit_plant_count(batch_name, new_count)
                    print(f"Batch {batch_name} plant count has been updated to {new_count}")
                except Exception as e:
                    print(f"Error: {e}")

            else:
                print("Invalid input homie, try 'name', 'strain', or 'plant count'")

        elif choice == "4":
            batch_name = input("What batch do you want to move? ")
            new_room = input("Where would you like to move the batch? ")
            try:
                move_batch(batch_name, new_room)
                print(f"Batch {batch_name} is now in {new_room}")
            except Exception as e:
                print(f"Error:{e}")
        elif choice == "5":
            batch_name = input("Which batch is on the chopping block today? ")
            try:
                delete_batch(batch_name)
                print(f"{batch_name} has been sacrificed to the gods of weed")
            except Exception as e:
                print(f"Error:{e}")

        elif choice == "6":
            batch_name = input("What batch are we harvesting today? ")
            try:
                harvest_batch(batch_name)
                print(f"{batch_name} has been harvested!")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "7":
            return

        else:
            print("Invalid choice hombre, try a number 1-7.")

def strain_menu():
    while True:
        choice = input("""
        What brings you in today?\n
        1. View strains
        2. Create strain
        3. Edit strain
        4. Delete strain
        5. Back to strain, uhhh I mean main
        """)

        if choice == "1":
            try:
                print(f"Here are all of your strains: {view_strains()}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            name = input("What's the name of this new and exciting strain? ")
            try:
                create_strain(name)
                print(f"{name} has been created. May it test 30%+ and get 4 lbs a light, Amen.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            old_name = input("What strain do you want to change? ")
            new_name = input("What is its new name? I hope the breeder knows about this... ")
            try:
                edit_strains(old_name, new_name)
                print(f"From this day forth, {old_name} will now be {new_name}. Now it will surely sell")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            name = input("What strain do you want to get rid of? ")
            try:
                delete_strains(name)
                print(f"Poor {name}... Never stood a chance.")
            except Exception as e:
                print(f"Error:{e}")

        elif choice == "5":
            return
        
        else:
            print("Invalid input hombre, try again.")

def task_menu():
    while True:
        choice = input("""
        What brings you in today?\n
        1. View tasks by room or batch
        2. Generate suggested tasks
        3. Create tasks
        4. Edit tasks
        5. Delete tasks
        6. Mark tasks completed
        7. Back to main
        """)

        if choice == "1":
            task_choice = input("Do you want to see tasks by room or batch? Try typing 'room' or 'batch' ")

            if task_choice == "room":
                room = input("Which room do you want to see tasks for? ")
                print(f"Here are the active tasks for {room}: {view_tasks_by_room(room)}")

            elif task_choice == "batch":
                batch = input("Which batch do you want to see tasks for? ")
                print(f"Here are the active tasks for {batch}: {view_tasks_by_batch(batch)}")

            else:
                print("Invalid input. Try using 'room' or 'batch'")
            
        elif choice == "2":
            batch = input("What batch do you want to generate tasks for? ")
            batch_info = get_batch_info(batch)
            if batch_info is None:
                print("Batch doesn't exist, try again.")
                continue
            print(batch_info)
            room_id = batch_info[3]
            room = get_room_name(room_id)

            suggested_schedule = task_scheduling(batch)

            choice = input(f"Here is your suggested schedule: {suggested_schedule}. Would you like to create these tasks and add them to your task list? ")

            if choice.lower() == "yes":
                for task_name, due_date in suggested_schedule:
                    create_task(room, batch, task_name, due_date)
                print("Tasks created!")

            else:
                print(f"Okay, no problem!")
                continue

            
        elif choice == "3":
            room = input("What room is this task for? ")
            batch = input("What batch is this task for? ")
            name = input("What is the task? ")
            due_date = input("When is it due? in yyyy-mm-dd format... or else ")
            try:
                create_task(room, batch, name, due_date)
                print(f"{name} has been added to your tasks.")
            except Exception as e:
                print(f"Error:{e}")

        elif choice == "4":
            room = input("What room are you trying to adjust tasks in? ")
            batch = input("What batch are you trying to adjust tasks for? ")
            old_task = input("What task do you want to change? ")
            new_task = input("What do you want the new task to be? ")
            try:
                edit_task(room, batch, old_task, new_task)
                print(f"{old_task} is now {new_task}")
            except Exception as e:
                print(f"Error: {e}")
            
        elif choice == "5":
            room = input("What room is the task in? ")
            batch = input("What batch is it for? ")
            task = input("What is the task you want to delete? ")
            try:
                delete_tasks(room, batch, task)
                print(f"{task} has been deleted.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "6":
            room = input("What room is this task in? ")
            batch = input("What batch is this task for? ")
            task = input("What task did you just finish? ")
            try:
                task_completed(room, batch, task)
                print(f"{task} in {room} is all done! Proud of u")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "7":
            return

        else:
            print("I got a task for you, try a valid input between 1-7.")


def main():
    facility = get_facility()
    
    if facility is None:
        first_use()
        facility = get_facility()

    home_facility = facility[1]

    print(f"Welcome back to {home_facility}!")
    main_menu()
        

    

    

main()

from repositories.facility_repository import get_facility
from db.connection import get_connection
from repositories.batch_repository import get_batch_info, get_batch_id
from datetime import timedelta

def task_scheduling(batch):
    batch_info = get_batch_info(batch)
    facility_info = get_facility()

    initialized_date = batch_info[5]
    clone_days = facility_info[2]
    veg_days = facility_info[3]
    flower_days = facility_info[4]


    transplant = initialized_date + timedelta(days=clone_days)
    top_date = transplant + timedelta(days=7)
    flip_date = transplant + timedelta(days=veg_days)
    prune = flip_date + timedelta(days=7)
    day_21 = flip_date + timedelta(days=21)
    day_42 = flip_date + timedelta(days=42)
    harvest_date = flip_date + timedelta(days=flower_days)
    bin_date = harvest_date + timedelta(days=14)

    suggested_schedule = [
    ("Transplant", transplant),
    ("Top", top_date),
    ("Flip", flip_date),
    ("Prune", prune),
    ("Day 21", day_21),
    ("Day 42", day_42),
    ("Harvest", harvest_date),
    ("Bin", bin_date)
    ]

    return suggested_schedule


    
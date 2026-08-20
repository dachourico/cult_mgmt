import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg.connect(DATABASE_URL)

# access via from db.connection import get_connection

"""
access like this
with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SQL query goes here")
        rows = cur.fetchall()

        for row in rows:
            print(row)
"""
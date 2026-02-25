import psycopg2
import os
from decimal import Decimal
from datetime import date, datetime

def serialize_value(value):
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, Decimal):
        return float(value)
    return value

def execute_query(sql):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    # 🔥 serialize everything for JSON safety
    serialized_rows = [
        [serialize_value(cell) for cell in row]
        for row in rows
    ]

    cur.close()
    conn.close()

    return serialized_rows
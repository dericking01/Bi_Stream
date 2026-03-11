import psycopg2
import os
from datetime import datetime

def check_db_connection():
    try:
        print(f"[{datetime.now()}] Attempting to connect to database...")
        print(f"  Host: {os.getenv('DB_HOST')}")
        print(f"  Port: {os.getenv('DB_PORT')}")
        print(f"  Database: {os.getenv('DB_NAME')}")
        print(f"  User: {os.getenv('DB_USER')}")
        
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()
        
        print(f"\n✅ SUCCESS: Connected to database!")
        print(f"   Current DB Time: {result[0]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: Cannot connect to database!")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_db_connection()
    exit(0 if success else 1)

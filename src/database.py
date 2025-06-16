import pymysql
from dotenv import load_dotenv
import os
# Carga las variables del archivo .env
load_dotenv()

conn = pymysql.connect(
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD"),
    host = os.getenv("DB_HOST"),
    port = int(os.getenv("DB_PORT")),
    database = os.getenv("DB_NAME")
)

def save_url(original_url, short_url):
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO urls (orig_url, short_url)
            VALUES (%s, %s)
        """, (original_url, short_url))
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error inserting into database: {e}")
    finally:
        cur.close()

def get_url(short_url):
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT orig_url FROM urls WHERE short_url = %s
        """, (short_url,))
        row = cur.fetchone()
        return row[0] if row else None
    except pymysql.MySQLError as e:
        print(f"Error querying database: {e}")
        return None
    finally:
        cur.close()
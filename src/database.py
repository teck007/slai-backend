import mariadb

conn = mariadb.connect(
    user="root",
    password="",
    host="127.0.0.1",
    port=3306,
    database="slai"
)

def save_url(original_url, short_url):
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO urls (orig_url, short_url)
            VALUES (?, ?)
        """, (original_url, short_url))
        conn.commit()
    except mariadb.Error as e:
        print(f"Error inserting into database: {e}")
    finally:
        cur.close()

def get_url(short_url):
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT orig_url FROM urls WHERE short_url = ?
        """, (short_url,))
        row = cur.fetchone()
        return row[0] if row else None
    except mariadb.Error as e:
        print(f"Error querying database: {e}")
        return None
    finally:
        cur.close()
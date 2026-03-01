# Importa la librería pymysql para interactuar con MySQL
import pymysql
# Importa load_dotenv para cargar variables de entorno desde un archivo .env
from dotenv import load_dotenv
import os
# Carga las variables del archivo .env en el entorno
load_dotenv()

# Establece la conexión a la base de datos usando las variables de entorno
def get_connection():
    return pymysql.connect(
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        host = os.getenv("DB_HOST"),
        port = int(os.getenv("DB_PORT")),
        database = os.getenv("DB_NAME")
        )

# Guarda URL original y su versión corta en la base de datos
def save_url(original_url, short_url):
    conn = get_connection()
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

# Recupera la URL original a partir de la URL corta
def get_url(short_url):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT orig_url FROM urls WHERE short_url = %s
            """, (short_url,))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    except pymysql.MySQLError as e:
        print(f"Error querying database: {e}")
        return None
    finally:
        cur.close()

# Busca la URL corta correspondiente a una URL original
def find_url(url):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
                SELECT short_url FROM urls WHERE orig_url = %s
                """, (url,))
        if cur.rowcount > 0:
            return str(cur.fetchone()[0])
        return None
    except pymysql.MySQLError as e:
        print(f"Error querying database: {e}")
    finally:
        cur.close()
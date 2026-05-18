from mysql.connector import pooling
from config import DB_CONFIG

# Connection pool for efficiency
pool = pooling.MySQLConnectionPool(
    pool_name="support_pool",
    pool_size=10,
    **DB_CONFIG
)

def get_connection():
    return pool.get_connection()

def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        
        # If SELECT query → return data
        if fetch:
            return cursor.fetchall()
        
        # If INSERT/UPDATE/DELETE → commit changes
        conn.commit()   # ⭐ REQUIRED to persist DB changes
        
        return None
    finally:
        cursor.close()
        conn.close()
import mysql.connector

def main():
    config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "Bhava@303030",
        "database": "support_tool"
    }
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print("--- Localhost Users ---")
        for u in users:
            print(f"user_name: {repr(u.get('user_name'))}, password: {repr(u.get('password'))}")
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error connecting to localhost DB:", e)

if __name__ == "__main__":
    main()

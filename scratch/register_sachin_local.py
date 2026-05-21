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
        cursor = conn.cursor()
        
        # Check if already exists
        cursor.execute("SELECT 1 FROM users WHERE user_name = 'sachin532210@gmail.com'")
        row = cursor.fetchone()
        
        if not row:
            insert_query = """
                INSERT INTO users (project_user_name, user_name, password, user_role)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, ("SACHIN A", "sachin532210@gmail.com", "admin123", "ADMIN"))
            conn.commit()
            print("Successfully registered Sachin on localhost database.")
        else:
            print("Sachin already exists in localhost database.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error registering user on localhost DB:", e)

if __name__ == "__main__":
    main()

import mysql.connector
import traceback

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
        
        query = """
            SELECT project_user_name, user_role, password
            FROM users
            WHERE user_name = %s
        """
        cursor.execute(query, ("sachin532210@gmail.com",))
        rows = cursor.fetchall()
        
        print("Rows fetched:", rows)
        if rows:
            user = rows[0]
            print("project_user_name:", repr(user.get("project_user_name")))
            print("user_role:", repr(user.get("user_role")))
            print("password:", repr(user.get("password")))
            
        cursor.close()
        conn.close()
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()

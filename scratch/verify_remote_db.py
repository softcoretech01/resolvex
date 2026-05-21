import mysql.connector

config = {
    "host": "187.127.131.38",
    "port": 3310,
    "user": "root",
    "password": "ResolveX_Pass#2026",
    "database": "support_tool"
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)

    # 1. Check sql_script column type
    cursor.execute("DESCRIBE ticket_master")
    cols = cursor.fetchall()
    for col in cols:
        if col['Field'] == 'sql_script':
            print(f"[sql_script column] Type: {col['Type']}, Null: {col['Null']}")

    # 2. Check if sachin exists in users table
    cursor.execute("SELECT user_name, project_user_name, user_role, password FROM users WHERE user_name = 'sachin532210@gmail.com'")
    rows = cursor.fetchall()
    if rows:
        u = rows[0]
        print(f"[users table] Found: {u['user_name']} | Name: {u['project_user_name']} | Role: {u['user_role']} | Pass: {u['password']}")
    else:
        print("[users table] sachin532210@gmail.com NOT FOUND in remote DB")

    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)

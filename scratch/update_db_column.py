import mysql.connector

def update_db(config, name):
    print(f"--- Updating database: {name} ({config['host']}:{config['port']}) ---")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        # Check current column type
        cursor.execute("DESCRIBE ticket_master")
        columns = cursor.fetchall()
        sql_script_col = None
        for col in columns:
            if col['Field'] == 'sql_script':
                sql_script_col = col
                break
        
        if sql_script_col:
            print(f"Current sql_script column type: {sql_script_col['Type']}")
            if 'mediumtext' not in sql_script_col['Type'].lower() and 'longtext' not in sql_script_col['Type'].lower():
                print("Altering column to MEDIUMTEXT...")
                cursor.execute("ALTER TABLE ticket_master MODIFY COLUMN sql_script MEDIUMTEXT NULL;")
                conn.commit()
                print("Successfully altered column.")
            else:
                print("Column is already MEDIUMTEXT/LONGTEXT.")
        else:
            print("sql_script column does not exist! Creating as MEDIUMTEXT...")
            cursor.execute("ALTER TABLE ticket_master ADD COLUMN sql_script MEDIUMTEXT NULL;")
            conn.commit()
            print("Successfully added column.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error:", e)

def main():
    # Local DB config
    local_config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "Bhava@303030",
        "database": "support_tool"
    }
    
    # Remote DB config
    remote_config = {
        "host": "187.127.131.38",
        "port": 3310,
        "user": "root",
        "password": "ResolveX_Pass#2026",
        "database": "support_tool"
    }
    
    update_db(local_config, "Localhost")
    update_db(remote_config, "Remote")

if __name__ == "__main__":
    main()

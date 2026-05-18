from db import execute_query
import traceback

def migrate():
    try:
        print("Adding total_time_spent column to ticket_master...")
        execute_query("ALTER TABLE ticket_master ADD COLUMN total_time_spent VARCHAR(255) NULL AFTER actual_time_spent")
        print("Success!")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("Column already exists.")
        else:
            traceback.print_exc()
            print(f"Error: {e}")

if __name__ == "__main__":
    migrate()

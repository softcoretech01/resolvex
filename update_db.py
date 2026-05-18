from db import execute_query

queries = [
    "ALTER TABLE ticket_master ADD COLUMN total_time_spent VARCHAR(255) NULL;",
    "ALTER TABLE ticket_master ADD COLUMN actual_time_spent VARCHAR(255) NULL;",
    "ALTER TABLE ticket_master ADD COLUMN db_changes TEXT NULL;",
    "ALTER TABLE ticket_master ADD COLUMN code_changes TEXT NULL;",
    "ALTER TABLE ticket_master ADD COLUMN reported_person VARCHAR(255) NULL;",
    "ALTER TABLE ticket_master ADD COLUMN short_name VARCHAR(100) NULL;",
    "ALTER TABLE ticket_master ADD COLUMN affected_user VARCHAR(255) NULL;",
    "ALTER TABLE ticket_master ADD COLUMN environment VARCHAR(255) NULL;",
    "ALTER TABLE ticket_master ADD COLUMN sql_script TEXT NULL;",
    "ALTER TABLE ticket_master ADD COLUMN sql_attachment VARCHAR(255) NULL;"
]

print("Starting database update...")

for query in queries:
    try:
        execute_query(query)
        print(f"SUCCESS: {query}")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print(f"INFO: Column already exists in query: {query}")
        else:
            print(f"ERROR: {e}")

print("\nDatabase update complete. You can now refresh your browser.")

from db import execute_query
import json

try:
    desc = execute_query("DESCRIBE modules", fetch=True)
    print("Schema:")
    print(json.dumps(desc, indent=2))
    
    rows = execute_query("SELECT * FROM modules", fetch=True)
    print("\nData:")
    print(json.dumps(rows, indent=2))
except Exception as e:
    print(f"Error: {e}")

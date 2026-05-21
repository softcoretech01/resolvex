import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import execute_query

def main():
    try:
        users = execute_query("SELECT * FROM users WHERE user_name LIKE '%sachin%'", fetch=True)
        print("--- Sachin Details ---")
        for u in users:
            print(f"user_name (repr): {repr(u.get('user_name'))}")
            print(f"password (repr): {repr(u.get('password'))}")
            print(f"project_user_name (repr): {repr(u.get('project_user_name'))}")
            print(f"user_role (repr): {repr(u.get('user_role'))}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()

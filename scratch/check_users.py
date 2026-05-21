import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import execute_query

def main():
    try:
        # Check all users
        users = execute_query("SELECT * FROM users", fetch=True)
        print("--- Users Table ---")
        for u in users:
            print(f"Username/Email: {u.get('user_name')}, Name: {u.get('project_user_name')}, Role: {u.get('user_role')}, Password: {u.get('password')}")
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()

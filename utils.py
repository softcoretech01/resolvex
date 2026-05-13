from db import execute_query

def next_code(table, code_prefix, id_column):
    next_id = execute_query(f"SELECT IFNULL(MAX({id_column}),0)+1 AS next_id FROM {table}", fetch=True)[0]["next_id"]
    return f"{code_prefix}{str(next_id).zfill(5)}"

def format_status(rows, key="status"):
    for row in rows:
        row[key] = "Active" if row[key] == 1 else "Inactive"
    return rows


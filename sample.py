from db import execute_query

rows = execute_query("""
    SELECT 
        p.project_code, p.project_name, p.client_id, c.client_name,
        p.project_type_id, pt.project_type_name,
        p.category, p.num_users, p.effective_from, p.effective_to,
        p.project_description, p.modules,
        p.database_type, p.front_end_tech_stack, p.back_end_tech_stack,
        p.status
    FROM project_master p
    LEFT JOIN client_master c ON p.client_id = c.client_id
    LEFT JOIN project_type_master pt ON p.project_type_id = pt.project_type_id
""", fetch=True)

print(rows)

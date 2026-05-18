

from fastapi import APIRouter, Request, Query, HTTPException
from db import execute_query
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from db import get_connection
import os
from fastapi.templating import Jinja2Templates
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

# Only import if you actually use Jinja2Templates in a route:

# Only import if you actually use Jinja2Templates in a route:
# from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Common APIs"])

# Serve the all-tickets changes report page
@router.get("/pages/changes-report", response_class=HTMLResponse)
def changes_report_page(request: Request):
    return Jinja2Templates(directory="templates").TemplateResponse("ChangesReport.html", {"request": request})
@router.api_route("/test_insert_sample_log", methods=["GET", "POST"])
def test_insert_sample_log():
    sample_db_change = "Added new column to users table."
    sample_code_change = "Refactored login logic for better security."
    now = "03-03-2026 10:00 AM"
    user = "TestUser"
    entry_db = f"""
#############################################################\n- {now} - {user}\n{sample_db_change}\n"""
    entry_code = f"""
#############################################################\n- {now} - {user}\n{sample_code_change}\n"""
    # Insert a new ticket with these logs (or update the first ticket if exists)
    rows = execute_query("SELECT ticket_code FROM ticket_master LIMIT 1", fetch=True)
    if rows:
        code = rows[0]["ticket_code"]
        execute_query(
            "UPDATE ticket_master SET db_changes=%s, code_changes=%s WHERE ticket_code=%s",
            (entry_db, entry_code, code)
        )
    else:
        # Insert a new ticket (minimal fields)
        execute_query(
            "INSERT INTO ticket_master (ticket_code, db_changes, code_changes, reported_person, reported_date, issue_short, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            ("T1000", entry_db, entry_code, user, now, "Sample Issue", "Open")
        )
    return {"status": "sample log inserted"}

# -------------------------------
# Clients
# -------------------------------
@router.get("/clients")
def get_clients_api():
    try:
        rows = execute_query(
            "SELECT client_id AS id, client_name AS name FROM client_master WHERE status = 1",
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Project types by category
# -------------------------------
@router.get("/project_types/{category}")
def get_project_types_api(category: int):
    try:
        rows = execute_query(
            "SELECT project_type_id AS id, project_type_name AS name FROM project_type_master WHERE category = %s AND status = 1",
            (category,),
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Modules dropdown
# -------------------------------
@router.get("/modules_dropdown")
def get_modules_api():
    try:
        rows = execute_query(
            "SELECT module_type_id AS id, module_type_name AS name FROM module_type_master WHERE status = 1",
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Databases dropdown
@router.get("/databases")
def get_databases_api():
    try:
        rows = execute_query(
            "SELECT database_type_id AS id, database_type_name AS name FROM database_type_master WHERE status = 1",
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Frontend tech stacks
@router.get("/frontend_techs")
def get_frontend_techs_api():
    try:
        rows = execute_query(
            "SELECT front_end_tech_stack_id AS id, front_end_tech_stack_name AS name FROM frontend_tech_stack_master WHERE status = 1",
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Backend tech stacks
@router.get("/backend_techs")
def get_backend_techs_api():
    try:
        rows = execute_query(
            "SELECT tech_stack_id AS id, tech_stack_name AS name FROM backend_tech_stack_master WHERE status = 1",
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Projects dropdown
@router.get("/projects_dropdown")
def get_projects_api():
    try:
        rows = execute_query(
            "SELECT project_id AS id, project_name AS name FROM project_master WHERE status = 1",
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Modules by project
@router.get("/project-users/modules/{project_id}")
def get_modules_by_project(project_id: int):
    try:
        rows = execute_query(
            """
            SELECT module_id AS id, module_name AS name 
            FROM modules 
            WHERE project_id = %s AND status = 1
            """,
            (project_id,),
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Menus by modules
@router.get("/project-users/menus", summary="Get menus by module IDs")
def get_menus_by_modules(module_ids: str = Query(..., description="Comma-separated module IDs")):
    try:
        module_list = [int(x) for x in module_ids.split(",") if x.isdigit()]
        if not module_list:
            return []  

        placeholders = ",".join(["%s"] * len(module_list))
        query = f"""
            SELECT menu_id AS id, menu_name AS name
            FROM menu_master
            WHERE module_name IN ({placeholders}) AND status = 1
        """
        rows = execute_query(query, tuple(module_list), fetch=True)
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menus: {str(e)}")

@router.get("/modules/for-menu", summary="Get modules for dropdown")
def get_modules_dropdown():
    try:
        rows = execute_query(
            "SELECT module_id AS id, module_name AS name FROM modules ORDER BY module_name ASC",
            fetch=True
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching modules: {str(e)}")

# -------------------------------------------------------------
# Changes log report (database-backed using execute_query)
# -------------------------------------------------------------
@router.get("/changes_report")
def get_changes_report():
    rows = execute_query(
        """
        SELECT db_changes, code_changes, tm.assigned_to_code, pu.project_user_name AS assigned_to_name
        FROM ticket_master tm
        LEFT JOIN project_users pu ON tm.assigned_to_code = pu.project_user_code
        WHERE (db_changes IS NOT NULL AND db_changes <> '')
           OR (code_changes IS NOT NULL AND code_changes <> '')
        ORDER BY ticket_id DESC
        """,
        fetch=True
    )

    def parse_logs(log_entries, assigned_to_name):
        logs = []
        for entry in log_entries:
            entry = entry.strip()
            if not entry:
                continue
            lines = entry.split("\n")
            date = ""
            time = ""
            content = ""
            if len(lines) >= 2:
                meta = lines[1].strip()
                if meta.startswith("-"):
                    meta = meta[1:].strip()
                # meta format: 03-2026 01:57 AM - Juli or 03-03-2026 10:00 AM - TestUser
                reported_by = ''
                if ' - ' in meta:
                    meta_main, reported_by = meta.rsplit(' - ', 1)
                    meta_main_parts = meta_main.strip().split()
                    if len(meta_main_parts) >= 2:
                        date = meta_main_parts[0]
                        time = ' '.join(meta_main_parts[1:])
                    else:
                        date = meta_main.strip()
                        time = ''
                else:
                    date = meta.strip()
                    time = ''
                content = "\n".join(lines[2:]).strip()
            else:
                content = lines[0].strip()
            if date or assigned_to_name or content:
                logs.append({
                    "date": date,
                    "time": time,
                    "assigned_to": assigned_to_name or '',
                    "content": content,
                })
        return logs

    db_logs = []
    code_logs = []
    for r in rows:
        assigned_to_name = r.get("assigned_to_name", "")
        if r["db_changes"] and r["db_changes"].strip():
            entries = [("#############################################################" + entry).strip() for entry in r["db_changes"].split("#############################################################") if entry.strip()]
            db_logs.extend(parse_logs(entries, assigned_to_name))
        if r["code_changes"] and r["code_changes"].strip():
            entries = [("#############################################################" + entry).strip() for entry in r["code_changes"].split("#############################################################") if entry.strip()]
            code_logs.extend(parse_logs(entries, assigned_to_name))

    def log_sort_key(log):
        # Combine date and time for sorting, fallback to empty string if missing
        return f"{log['date']} {log['time']}"

    db_logs_sorted = sorted(db_logs, key=log_sort_key, reverse=True)
    code_logs_sorted = sorted(code_logs, key=log_sort_key, reverse=True)
    return {
        "db_changes": db_logs_sorted,
        "code_changes": code_logs_sorted
    }

# Simple test route to verify router registration
@router.get("/test_alive")
def test_alive():
    return {"status": "alive"}


# extra page routes will be appended below

@router.get("/project-module-type/{project_id}", summary="Get module type by project")
def get_module_type_by_project(project_id: int):
    try:
        rows = execute_query(
            "SELECT modules AS module_type_id FROM project_master WHERE project_id=%s AND status=1",
            (project_id,),
            fetch=True
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Project not found")

        module_type_id = rows[0]["module_type_id"]
        type_rows = execute_query(
            "SELECT module_type_id AS id, module_type_name AS name FROM module_type_master WHERE module_type_id=%s AND status=1",
            (module_type_id,),
            fetch=True
        )
        if not type_rows:
            raise HTTPException(status_code=404, detail="Module type not found")

        return type_rows[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Menus by project and modules
@router.get("/project-users/menus/{project_id}", summary="Get menus by project and module IDs")
def get_menus_by_project_and_modules(
    project_id: int,
    module_ids: str = Query(..., description="Comma-separated module IDs")
):
    try:
        module_list = [int(x) for x in module_ids.split(",") if x.isdigit()]
        if not module_list:
            return []

        placeholders = ",".join(["%s"] * len(module_list))
        query = f"""
            SELECT menu_id AS id, menu_name AS name
            FROM menu_master
            WHERE module_name IN ({placeholders})
              AND project_id = %s
              AND status = 1
        """
        params = tuple(module_list) + (project_id,)
        rows = execute_query(query, params, fetch=True)
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menus: {str(e)}")


# -------------------------------------------------------------
# Misc utilities
# -------------------------------------------------------------
@router.post("/save_changes")
def save_changes(data: dict):
    # append database and code change notes to plain text log files
    with open("DBCHANGELOG.md","a",encoding="utf-8") as f:
        f.write("\n" + data.get("db_changes",""))

    with open("CHANGELOG.md","a",encoding="utf-8") as f:
        f.write("\n" + data.get("code_changes",""))

    return {"status":"saved"}


# additional page endpoints for standalone view
import os
from fastapi.responses import HTMLResponse
from db import get_connection

# Only import if you actually use Jinja2Templates in a route:
# from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


# 🔹 Page for DB changes
@router.get("/pages/db-changes", response_class=HTMLResponse)
def db_changes_page(request: Request):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT db_changes 
        FROM ticket_master
        WHERE db_changes IS NOT NULL 
        AND db_changes <> ''
        ORDER BY updated_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    logs = "\n".join([r["db_changes"] for r in rows])
    return templates.TemplateResponse(
        "db_changes.html",
        {"request": request, "logs": logs}
    )

# 🔹 Page for Code changes
@router.get("/pages/code-changes", response_class=HTMLResponse)
def code_changes_page(request: Request):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT code_changes 
        FROM ticket_master
        WHERE code_changes IS NOT NULL 
        AND code_changes <> ''
        ORDER BY updated_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    logs = "\n".join([r["code_changes"] for r in rows])
    return templates.TemplateResponse(
        "code_changes.html",
        {"request": request, "logs": logs}
    )

# 🔵 SAVE DB & CODE CHANGES (optional logging hook)
@router.post("/save_changes")
def save_changes(data: dict):
    return {"status": "ok"}   # no file logging needed anymore



@router.get("/code_changes")
def get_code_changes():
    rows = execute_query(
        """
        SELECT ticket_code, code_changes
        FROM ticket_master
        WHERE code_changes IS NOT NULL AND code_changes <> ''
        ORDER BY ticket_id DESC
        """,
        fetch=True
    )
    return rows or []

@router.get("/export_changes_pdf")
def export_pdf(type: str = Query("all")):
    report = get_changes_report()
    formatted_logs = []
    
    if type in ["all", "db"]:
        for log in report.get("db_changes", []):
            formatted_logs.append("#############################################################")
            date_line = f"- {log.get('date', '')} {log.get('time', '')}"
            if log.get("assigned_to"):
                date_line += f" - {log.get('assigned_to')}"
            formatted_logs.append(date_line)
            formatted_logs.append("DB Change:")
            formatted_logs.append(log.get('content', ''))
            formatted_logs.append("")
            
    if type in ["all", "code"]:
        for log in report.get("code_changes", []):
            formatted_logs.append("#############################################################")
            date_line = f"- {log.get('date', '')} {log.get('time', '')}"
            if log.get("assigned_to"):
                date_line += f" - {log.get('assigned_to')}"
            formatted_logs.append(date_line)
            formatted_logs.append("Code Change:")
            formatted_logs.append(log.get('content', ''))
            formatted_logs.append("")
            
    logs_str = "\n".join(formatted_logs)
    
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(file.name, pagesize=letter)
    y = 750
    for line in logs_str.split("\n"):
        c.drawString(40, y, line[:120])
        y -= 14
        if y < 40:
            c.showPage()
            y = 750
    c.save()
    return FileResponse(file.name, filename=f"ChangeLog_{type}.pdf")

@router.get("/download_changes")
def download_changes(type: str = Query("all")):
    report = get_changes_report()
    formatted_logs = []
    
    if type in ["all", "db"]:
        for log in report.get("db_changes", []):
            formatted_logs.append("#############################################################")
            date_line = f"- {log.get('date', '')} {log.get('time', '')}"
            if log.get("assigned_to"):
                date_line += f" - {log.get('assigned_to')}"
            formatted_logs.append(date_line)
            formatted_logs.append("DB Change:")
            formatted_logs.append(log.get('content', ''))
            formatted_logs.append("")
            
    if type in ["all", "code"]:
        for log in report.get("code_changes", []):
            formatted_logs.append("#############################################################")
            date_line = f"- {log.get('date', '')} {log.get('time', '')}"
            if log.get("assigned_to"):
                date_line += f" - {log.get('assigned_to')}"
            formatted_logs.append(date_line)
            formatted_logs.append("Code Change:")
            formatted_logs.append(log.get('content', ''))
            formatted_logs.append("")
            
    logs_str = "\n".join(formatted_logs)
    
    return PlainTextResponse(logs_str, headers={
        "Content-Disposition": f"attachment; filename=ChangeLog_{type}.txt"
    })

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form

# NOTE: The ticket_master table should include an 'affected_user' VARCHAR column.
# You can add it with:
#   ALTER TABLE ticket_master ADD COLUMN affected_user VARCHAR(255) NULL;
# The API and UI expect this field to exist.
from db import execute_query, get_connection
from utils import next_code
import traceback
import os
import shutil
from typing import Optional
from datetime import datetime

router = APIRouter(tags=["Tickets"])

# Directory to store uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----------------------------------------------
# DROPDOWN ENDPOINTS (Unchanged)
# ----------------------------------------------

@router.get("/dropdown/projects", summary="Projects dropdown for tickets")
def tickets_dropdown_projects():
    try:
        return execute_query("SELECT project_code AS code, project_name AS name FROM project_master WHERE status = 1 ORDER BY project_name", fetch=True)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dropdown/module-types", summary="Module types dropdown for tickets")
def tickets_dropdown_module_types():
    try:
        return execute_query("SELECT module_type_code AS code, module_type_name AS name FROM module_type_master WHERE status = 1 ORDER BY module_type_name", fetch=True)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dropdown/modules", summary="Modules dropdown (filtered by project)")
def tickets_dropdown_modules(project_code: str = Query(...)):
    try:
        rows = execute_query("SELECT module_code AS code, module_name AS name FROM modules WHERE project_code = %s AND status = 1 ORDER BY module_name", (project_code,), fetch=True)
        
        nicknames = {
            "Finance": "FM",
            "Procurement": "PM",
            "Claim": "CM",
            "Sales": "SM",
            "Tank Master": "TM",
            "Tank Inspection": "TI"
        }
        
        for row in rows:
            name = row["name"]
            if name in nicknames:
                row["name"] = f"{nicknames[name]} - {name}"
                
        return rows
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dropdown/clients", summary="Clients dropdown for reported users")
def tickets_dropdown_clients():
    try:
        return execute_query("SELECT client_code AS code, client_name AS name FROM client_master WHERE status = 1 ORDER BY client_name", fetch=True)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dropdown/project-users", summary="Project users dropdown (filtered by project)")
# project_code is now optional; when omitted we return all active users

def tickets_dropdown_project_users(project_code: Optional[str] = Query(None)):
    try:
        if project_code:
            users = execute_query(
                "SELECT project_user_code AS code, project_user_name AS name FROM project_users "
                "WHERE project_code = %s AND status = 1 ORDER BY project_user_name",
                (project_code,), fetch=True
            )
            if not users:
                # Fallback: return all active users if none found for project
                users = execute_query(
                    "SELECT project_user_code AS code, project_user_name AS name FROM project_users "
                    "WHERE status = 1 ORDER BY project_user_name",
                    fetch=True
                )
            return users
        else:
            # no filter – return everyone active
            return execute_query(
                "SELECT project_user_code AS code, project_user_name AS name FROM project_users "
                "WHERE status = 1 ORDER BY project_user_name",
                fetch=True
            )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------
# MAIN CRUD OPERATIONS
# ----------------------------------------------
@router.get("", summary="Get all tickets")
@router.get("/", summary="Get all tickets")
def get_tickets():
    try:
        # UPDATED: Select reported_person instead of reported_time
        query = """
            SELECT
                tm.ticket_id, tm.ticket_code, tm.cif_no, tm.issue_short, tm.issue_desc,
                tm.project_code, p.project_name,
                tm.module_type_code, mt.module_type_name,
                tm.module_code, m.module_name,
                tm.screen, 
                tm.reported_user_code, c.client_name AS reported_user_name,
                tm.assigned_to_code, au.project_user_name AS assigned_to_name,
                DATE_FORMAT(tm.reported_date, '%Y-%m-%d') AS reported_date,
                TIME_FORMAT(tm.reported_date, '%H:%i:%s') AS reported_time,
                tm.reported_person,
                tm.priority, tm.severity,
                tm.affected_user,
                DATE_FORMAT(tm.target_date, '%Y-%m-%d') AS target_date,
                tm.attachment, tm.root_cause, tm.solution, tm.status, tm.actual_time_spent, tm.total_time_spent,
                tm.db_changes, tm.code_changes, tm.environment, tm.sql_script, tm.sql_attachment, tm.short_name,
                tm.created_at, tm.updated_at
            FROM ticket_master tm
            LEFT JOIN project_master p      ON tm.project_code = p.project_code
            LEFT JOIN module_type_master mt ON tm.module_type_code = mt.module_type_code
            LEFT JOIN modules m             ON tm.module_code = m.module_code
            LEFT JOIN client_master c       ON tm.reported_user_code = c.client_code
            LEFT JOIN project_users au      ON tm.assigned_to_code = au.project_user_code
            ORDER BY tm.ticket_id DESC
        """
        return execute_query(query, fetch=True)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error fetching tickets")


@router.post("", summary="Add a new ticket")
@router.post("/", summary="Add a new ticket")
def add_ticket(
    project_code: str = Form(...),
    module_type_code: str = Form(...),
    module_code: str = Form(...),
    screen: Optional[str] = Form(None),
    issue_short: str = Form(...),
    reported_user_code: str = Form(...),
    priority: str = Form(...),
    severity: str = Form(...),
    affected_user: Optional[str] = Form(None),
    issue_desc: Optional[str] = Form(None),
    reported_date: Optional[str] = Form(None),
    reported_person: Optional[str] = Form(None),
    target_date: Optional[str] = Form(None),
    assigned_to_code: Optional[str] = Form(None),
    environment: Optional[str] = Form(None),
    sql_script: Optional[str] = Form(None),
    short_name: Optional[str] = Form(None),
    attachment: Optional[list[UploadFile]] = File(None),
    sql_attachment: Optional[list[UploadFile]] = File(None)
):
    try:
        # 🔹 Generate ticket code
        ticket_code = next_code("ticket_master", "T", "ticket_id")

        # 🔹 Generate CIF from ticket
        numeric = ticket_code.replace("T", "")
        year = datetime.now().year
        cif_no = f"{year}-{numeric}"

        # 🔹 Handle multiple file uploads
        attachment_filenames = []
        if attachment:
            for file in attachment:
                safe_filename = f"{ticket_code}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, safe_filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                attachment_filenames.append(safe_filename)
        attachment_filename = ",".join(attachment_filenames) if attachment_filenames else None

        # 🔹 Handle SQL attachment uploads
        sql_attachment_filenames = []
        if sql_attachment:
            for file in sql_attachment:
                safe_filename = f"SQL_{ticket_code}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, safe_filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                sql_attachment_filenames.append(safe_filename)
        sql_attachment_filename = ",".join(sql_attachment_filenames) if sql_attachment_filenames else None

        # 🔹 Insert into DB (NOW WITH CIF)
        execute_query(
            """
            INSERT INTO ticket_master (
                ticket_code, cif_no,
                project_code, module_type_code, module_code, screen,
                issue_short, issue_desc, reported_user_code,
                reported_date, reported_person,
                priority, severity, affected_user, target_date,
                assigned_to_code, attachment, sql_attachment, status, environment, sql_script, short_name, created_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
            (
                ticket_code, cif_no,
                project_code, module_type_code, module_code, screen,
                issue_short, issue_desc, reported_user_code,
                reported_date, reported_person,
                priority, severity, affected_user, target_date,
                assigned_to_code, attachment_filename, sql_attachment_filename, "Open", environment, sql_script, short_name
            ),
        )

        return {
            "message": "Ticket added successfully",
            "ticket_code": ticket_code,
            "cif_no": cif_no
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}", summary="Get ticket by code")
def get_ticket_by_code(code: str):
    try:
        # UPDATED: Select reported_person
        rows = execute_query(
            """
            SELECT
                tm.ticket_id, tm.ticket_code, tm.cif_no, tm.issue_short, tm.issue_desc,
                tm.project_code, p.project_name,
                tm.module_type_code, mt.module_type_name,
                tm.module_code, m.module_name,
                tm.screen, 
                tm.reported_user_code, c.client_name AS reported_user_name,
                tm.assigned_to_code, au.project_user_name AS assigned_to_name,
                DATE_FORMAT(tm.reported_date, '%Y-%m-%d') AS reported_date,
                tm.reported_person, -- NEW
                tm.priority, tm.severity,
                tm.affected_user,
                DATE_FORMAT(tm.target_date, '%Y-%m-%d') AS target_date,
                tm.attachment, tm.root_cause, tm.solution, tm.status, tm.actual_time_spent, tm.total_time_spent,
                tm.db_changes, tm.code_changes, tm.environment, tm.sql_script, tm.sql_attachment, tm.short_name,
                tm.created_at, tm.updated_at
            FROM ticket_master tm
            LEFT JOIN project_master p      ON tm.project_code = p.project_code
            LEFT JOIN module_type_master mt ON tm.module_type_code = mt.module_type_code
            LEFT JOIN modules m             ON tm.module_code = m.module_code
            LEFT JOIN client_master c       ON tm.reported_user_code = c.client_code
            LEFT JOIN project_users au      ON tm.assigned_to_code = au.project_user_code
            WHERE tm.ticket_code = %s
            """,
            (code,), fetch=True
        )
        if not rows: raise HTTPException(status_code=404, detail="Ticket not found")
        return rows[0]
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{code}", summary="Update ticket")
def update_ticket(
    code: str,
    project_code: Optional[str] = Form(None),
    module_type_code: Optional[str] = Form(None),
    module_code: Optional[str] = Form(None),
    screen: Optional[str] = Form(None),
    issue_short: Optional[str] = Form(None),
    reported_user_code: Optional[str] = Form(None),
    priority: Optional[str] = Form(None),
    severity: Optional[str] = Form(None),
    affected_user: Optional[str] = Form(None),
    issue_desc: Optional[str] = Form(None),
    reported_date: Optional[str] = Form(None),
    reported_person: Optional[str] = Form(None),
    target_date: Optional[str] = Form(None),
    assigned_to_code: Optional[str] = Form(None),
    root_cause: Optional[str] = Form(None),
    solution: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    actual_time_spent: Optional[str] = Form(None),
    total_time_spent: Optional[str] = Form(None),
    db_changes: Optional[str] = Form(None),
    code_changes: Optional[str] = Form(None),
    environment: Optional[str] = Form(None),
    sql_script: Optional[str] = Form(None),
    short_name: Optional[str] = Form(None),
    updated_by: Optional[str] = Form("System"),
    attachment: Optional[list[UploadFile]] = File(None),
    sql_attachment: Optional[list[UploadFile]] = File(None)
):
    try:
        existing = execute_query("SELECT * FROM ticket_master WHERE ticket_code=%s", (code,), fetch=True)
        if not existing: raise HTTPException(status_code=404, detail="Ticket not found")
        row = existing[0]
        val = lambda new, old: new if new is not None else old
        current_attachment = row['attachment']
        if attachment:
            filenames = []
            for file in attachment:
                safe_filename = f"{code}_{file.filename}"
                with open(os.path.join(UPLOAD_DIR, safe_filename), "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                filenames.append(safe_filename)
            # Merge with existing attachments, avoid duplicates
            if current_attachment:
                existing_files = [f.strip() for f in current_attachment.split(',') if f.strip()]
                filenames = existing_files + [f for f in filenames if f not in existing_files]
            attachment_filename = ','.join(filenames)
        else:
            attachment_filename = current_attachment

        # 🔹 Handle SQL attachment uploads
        sql_attachment_filenames = []
        if sql_attachment:
            for file in sql_attachment:
                safe_filename = f"SQL_{code}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, safe_filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                sql_attachment_filenames.append(safe_filename)
            sql_attachment_filename = ",".join(sql_attachment_filenames)
        else:
            sql_attachment_filename = row.get('sql_attachment')

        now = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        user = reported_person or updated_by or "System"
        # Build changelogs
        db_changes_log = build_log(row.get('db_changes'), db_changes, now, user)
        code_changes_log = build_log(row.get('code_changes'), code_changes, now, user)
        execute_query(
            """
            UPDATE ticket_master SET
                project_code=%s, module_type_code=%s, module_code=%s, screen=%s,
                issue_short=%s, issue_desc=%s, reported_user_code=%s,
                reported_date=%s, reported_person=%s, priority=%s, severity=%s,
                affected_user=%s,  # <--- added placeholder
                target_date=%s, assigned_to_code=%s, attachment=%s,
                root_cause=%s, solution=%s, status=%s, actual_time_spent=%s, total_time_spent=%s,
                db_changes=%s, code_changes=%s, environment=%s, sql_script=%s, sql_attachment=%s, short_name=%s,
                updated_at=NOW()
            WHERE ticket_code=%s
            """,
            (
                val(project_code, row['project_code']),
                val(module_type_code, row['module_type_code']),
                val(module_code, row['module_code']),
                val(screen, row['screen']),
                val(issue_short, row['issue_short']),
                val(issue_desc, row['issue_desc']),
                val(reported_user_code, row['reported_user_code']),
                val(reported_date, row['reported_date']),
                val(reported_person, row['reported_person']),
                val(priority, row['priority']),
                val(severity, row['severity']),
                val(affected_user, row.get('affected_user')),
                val(target_date, row['target_date']),
                val(assigned_to_code, row['assigned_to_code']),
                attachment_filename,
                val(root_cause, row['root_cause']),
                val(solution, row['solution']),
                val(status, row['status']),
                val(actual_time_spent, row['actual_time_spent']),
                val(total_time_spent, row.get('total_time_spent')),
                db_changes_log,
                code_changes_log,
                val(environment, row.get('environment')),
                val(sql_script, row.get('sql_script')),
                sql_attachment_filename if sql_attachment else row.get('sql_attachment'),
                val(short_name, row.get('short_name')),
                code,
            ),
        )
        return {"message": "Ticket updated successfully", "code": code}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{code}", summary="Delete ticket")
def delete_ticket(code: str):
    try:
        existing = execute_query("SELECT attachment FROM ticket_master WHERE ticket_code=%s", (code,), fetch=True)
        if existing and existing[0]['attachment']:
             file_path = os.path.join(UPLOAD_DIR, existing[0]['attachment'])
             if os.path.exists(file_path): os.remove(file_path)

        execute_query("DELETE FROM ticket_master WHERE ticket_code=%s", (code,))
        return {"message": "Ticket deleted successfully"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --------- Printable endpoint ----------
@router.get("/print/{code}", summary="Printable ticket data")
def printable_ticket(code: str):
    try:
        row = execute_query("""
            SELECT
                tm.ticket_code,
                tm.cif_no,
                DATE_FORMAT(tm.reported_date,'%d-%b-%Y') AS reported_date,
                tm.priority,
                tm.severity,
                tm.affected_user,
                tm.issue_short,
                tm.issue_desc,
                tm.screen,
                tm.reported_person,
                c.client_name,
                au.project_user_name AS assigned_to,
                tm.root_cause,
                tm.solution,
                tm.status
            FROM ticket_master tm
            LEFT JOIN client_master c ON tm.reported_user_code=c.client_code
            LEFT JOIN project_users au ON tm.assigned_to_code=au.project_user_code
            WHERE tm.ticket_code=%s
        """,(code,),fetch=True)

        if not row:
            raise HTTPException(status_code=404, detail="Ticket not found")

        return row[0]

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# DB CHANGES API
@router.get("/api/changes_report/{ticket_code}")
def get_changes_report(ticket_code: str):
    row = execute_query(
        "SELECT db_changes, code_changes FROM ticket_master WHERE ticket_code=%s",
        (ticket_code,),
        fetch=True
    )
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db_changes = row[0]["db_changes"] or ""
    code_changes = row[0]["code_changes"] or ""
    db_logs = ["#############################################################" + entry for entry in db_changes.split("#############################################################") if entry.strip()]
    code_logs = ["#############################################################" + entry for entry in code_changes.split("#############################################################") if entry.strip()]
    return {
        "db_changes": db_logs,
        "code_changes": code_logs
    }

def build_log(old, new, now, user):
    # ignore empty input
    if new is None or not new.strip():
        return old

    # Fallbacks for user and now
    if not user:
        user = "System"
    if not now:
        from datetime import datetime
        now = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    entry = f"""
#############################################################
- {now} - {user}
{new.strip()}
"""

    # Always append, never overwrite
    if old and old.strip():
        return old.rstrip() + "\n" + entry
    else:
        return entry
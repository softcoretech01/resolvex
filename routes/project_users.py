from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from db import execute_query
from utils import next_code
import traceback

# ==========================================
# 1. DEFINE MODELS HERE (To fix the 422 Error)
# ==========================================
class ProjectUserCreate(BaseModel):
    project_code: str
    user_id: int            # <--- We now require user_id
    module_code: Optional[List[str]] = None
    status: Optional[int] = 1
    # We removed 'project_user_name' and 'email' because we fetch them on the backend now

class ProjectUserUpdate(BaseModel):
    project_code: Optional[str] = None
    user_id: Optional[int] = None
    module_code: Optional[List[str]] = None
    status: Optional[int] = None

# ==========================================
# 2. ROUTER LOGIC
# ==========================================
router = APIRouter(tags=["Project Users"])

# ---------------- HELPER: Fetch User Safely ----------------
def fetch_user_data(query_suffix, params=None, fetch_all=True):
    try:
        # Attempt 1: Try with 'support_tool.users'
        sql = f"SELECT project_user_id, project_user_name, user_name FROM support_tool.users {query_suffix}"
        return execute_query(sql, params, fetch=fetch_all)
    except Exception as e:
        print(f"DEBUG: 'support_tool.users' failed. Trying 'users' table...")
        try:
            # Attempt 2: Try local 'users' table
            sql = f"SELECT project_user_id, project_user_name, user_name FROM users {query_suffix}"
            return execute_query(sql, params, fetch=fetch_all)
        except Exception as e2:
            print(f"DEBUG: 'users' table also failed: {e2}")
            return []

# ---------------- OPTIONS ENDPOINTS (Dropdowns) ----------------
@router.get("/options/master-users", summary="Get users for dropdown")
def get_master_users_options():
    try:
        # Fetches ID and Name for the dropdown
        return fetch_user_data("ORDER BY project_user_name ASC")
    except Exception as e:
        traceback.print_exc()
        return []

@router.get("/options/projects", summary="Get active projects")
def get_projects_options():
    try:
        return execute_query(
            "SELECT project_code, project_name FROM project_master WHERE status=1 ORDER BY project_name ASC", 
            fetch=True
        )
    except Exception:
        return []

@router.get("/options/modules", summary="Get active modules")
def get_modules_options():
    try:
        return execute_query(
            "SELECT module_code, module_name FROM modules WHERE status=1 ORDER BY module_name ASC", 
            fetch=True
        )
    except Exception:
        return []


# ---------------- ADD (POST) ----------------
@router.post("/", summary="Assign a user to a project")
def add_project_user(data: ProjectUserCreate):
    try:
        # 1. Validate inputs
        if not data.user_id or not data.project_code:
            raise HTTPException(status_code=400, detail="Project and User Selection are required!")

        # 2. Fetch User Details from Master Table using the ID
        master_user = fetch_user_data("WHERE project_user_id=%s", (data.user_id,))
        
        if not master_user:
            raise HTTPException(status_code=404, detail="Selected user not found in master table!")
            
        user_name = master_user[0]['project_user_name']
        email = master_user[0]['user_name']  # user_name maps to email

        # 3. Check for Duplicate
        duplicate_check = execute_query(
            "SELECT COUNT(*) as cnt FROM project_users WHERE project_code=%s AND email=%s",
            (data.project_code, email),
            fetch=True
        )
        if duplicate_check and duplicate_check[0]["cnt"] > 0:
            raise HTTPException(status_code=400, detail=f"User '{user_name}' is already assigned to this project!")

        # 4. Insert into project_users (Copying the text data)
        code = next_code("project_users", "PU", "project_user_id")
        module_codes_str = ",".join(data.module_code) if data.module_code else None
        status_val = 1 if str(data.status).lower() in ["active", "1"] else 0

        execute_query(
            """
            INSERT INTO project_users 
                (project_user_code, project_code, project_user_name, email, module_codes, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (code, data.project_code, user_name, email, module_codes_str, status_val)
        )

        return {
            "message": f"User '{user_name}' assigned successfully!",
            "code": code
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error adding project user: {str(e)}")


# ---------------- GET ALL ----------------
@router.get("/", summary="Get all project users")
def get_project_users():
    try:
        rows = execute_query(
            """
            SELECT 
                pu.project_user_id,
                pu.project_user_code,
                pu.project_code,
                pm.project_name,
                pu.project_user_name,
                pu.email,
                pu.module_codes,
                pu.status,
                pu.created_at,
                pu.updated_at
            FROM project_users pu
            LEFT JOIN project_master pm 
                ON pu.project_code = pm.project_code
            ORDER BY pu.project_user_id DESC
            """,
            fetch=True
        )

        for r in rows:
            r["status"] = "Active" if r["status"] == 1 else "Inactive"
            if r["module_codes"]:
                mod_names = execute_query(
                    f"SELECT GROUP_CONCAT(module_name) as names FROM modules WHERE FIND_IN_SET(module_code, '{r['module_codes']}')",
                    fetch=True
                )
                r["modules"] = mod_names[0]["names"] if mod_names and mod_names[0]["names"] else "-"
                r["module_codes"] = r["module_codes"].split(",")
            else:
                r["modules"] = "-"
                r["module_codes"] = []

        return rows

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching project users: {str(e)}")


# ---------------- GET BY ID ----------------
@router.get("/id/{project_user_id}", summary="Get by ID")
def get_project_user_by_id(project_user_id: int):
    try:
        row = execute_query(
            """
            SELECT 
                pu.project_user_id,
                pu.project_code,
                pm.project_name,
                pu.project_user_name,
                pu.email,
                pu.module_codes,
                pu.status
            FROM project_users pu
            LEFT JOIN project_master pm ON pu.project_code = pm.project_code
            WHERE pu.project_user_id = %s
            """,
            (project_user_id,),
            fetch=True
        )

        if not row:
            raise HTTPException(status_code=404, detail="User assignment not found")

        user = row[0]
        user["status"] = "Active" if user["status"] == 1 else "Inactive"
        user["module_codes"] = user["module_codes"].split(",") if user["module_codes"] else []
        return user

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- UPDATE ----------------
@router.put("/{project_user_id}", summary="Update assignment")
def update_project_user(project_user_id: int, data: ProjectUserUpdate):
    try:
        exists = execute_query("SELECT * FROM project_users WHERE project_user_id=%s", (project_user_id,), fetch=True)
        if not exists:
            raise HTTPException(status_code=404, detail="Record not found")

        existing = exists[0]
        new_name = existing["project_user_name"]
        new_email = existing["email"]
        
        # If a NEW user_id is provided, fetch and update details
        if data.user_id:
            master_user = fetch_user_data("WHERE project_user_id=%s", (data.user_id,))
            if master_user:
                new_name = master_user[0]['project_user_name']
                new_email = master_user[0]['user_name']

        project_code_val = data.project_code or existing["project_code"]
        
        module_codes = (
            data.module_code if data.module_code is not None 
            else existing["module_codes"].split(",") if existing.get("module_codes") else []
        )
        module_codes_str = ",".join(module_codes) if module_codes else None
        status_val = data.status if data.status is not None else existing.get("status", 1)

        execute_query(
            """
            UPDATE project_users
            SET project_code=%s, project_user_name=%s, email=%s, module_codes=%s, status=%s, updated_at=NOW()
            WHERE project_user_id=%s
            """,
            (project_code_val, new_name, new_email, module_codes_str, status_val, project_user_id)
        )

        return {"message": "Project user updated successfully!"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating: {str(e)}")


# ---------------- DELETE ----------------
@router.delete("/{project_user_id}", summary="Delete assignment")
def delete_project_user(project_user_id: int):
    try:
        execute_query("DELETE FROM project_users WHERE project_user_id=%s", (project_user_id,))
        return {"message": "Deleted successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
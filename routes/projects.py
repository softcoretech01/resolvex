from fastapi import APIRouter, HTTPException
from models.projects import ProjectCreate, ProjectUpdate
from db import execute_query
from utils import next_code
import traceback


router = APIRouter(tags=["Projects"])

@router.get("", summary="Get all projects")
@router.get("/", summary="Get all projects")
def get_projects():
    try:
        query = """
            SELECT 
                p.project_code, p.project_name, 
                p.client_code, c.client_name,
                p.project_type_code, pt.project_type_name,
                p.category, p.num_users, p.effective_from, p.effective_to,
                p.project_description, 
                p.database_type_code, 
                p.front_end_tech_stack_code, fe.front_end_tech_stack_name AS front_end_tech_stack_name, 
                p.back_end_tech_stack_code, be.tech_stack_name AS back_end_tech_stack_name,
                p.status
            FROM project_master p
            LEFT JOIN client_master c ON p.client_code = c.client_code 
            LEFT JOIN project_type_master pt ON p.project_type_code = pt.project_type_code
            LEFT JOIN frontend_tech_stack_master fe ON p.front_end_tech_stack_code = fe.front_end_tech_stack_code 
            LEFT JOIN backend_tech_stack_master be ON p.back_end_tech_stack_code = be.tech_stack_code     
        """
        rows = execute_query(query, fetch=True)

        for r in rows:
            r["status"] = "Active" if r.get("status") == 1 else "Inactive"
            r["category"] = "New Development" if str(r.get("category")) == "0" else "Support"
        return rows
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error fetching projects")

@router.post("", summary="Add a new project")
@router.post("/", summary="Add a new project")
def add_project(data: ProjectCreate):
    try:
        if not data.project_name or not data.client_code or not data.category or not data.project_type_code or not data.status:
            raise HTTPException(status_code=400, detail="Project Name, Client Code, Category, Project Type, and Status are required!")

        category_val = int(data.category) if str(data.category).isdigit() else (0 if str(data.category).lower() in ["new", "new development"] else 1)
        if str(data.status).lower() in ["active", "1"]:
            status_val = 1
        else:
            status_val = 0

        project_code = next_code("project_master", "PR", "project_id")

        insert_query = """
            INSERT INTO project_master (
                project_code, project_name, client_code, category, project_type_code, num_users,
                effective_from, effective_to, project_description, 
                database_type_code, front_end_tech_stack_code, back_end_tech_stack_code, status
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        execute_query(insert_query, (
            project_code, data.project_name, data.client_code, category_val, data.project_type_code, data.num_users,
            data.effective_from, data.effective_to, data.project_description, 
            data.database_type_code, data.front_end_tech_stack_code, data.back_end_tech_stack_code, status_val
        ))

        return {"message": f"Project '{data.project_name}' added successfully!", "code": project_code}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error adding project: {str(e)}")


@router.put("/{code}", summary="Update project")
def update_project(code: str, data: ProjectUpdate):
    try:
        if not data.project_name or not data.client_code or not data.category or not data.project_type_code or not data.status:
            raise HTTPException(status_code=400, detail="Project Name, Client Code, Category, Project Type, and Status are required!")

        category_val = int(data.category) if str(data.category).isdigit() else (0 if str(data.category).lower() in ["new", "new development"] else 1)
        if str(data.status).lower() in ["active", "1"]:
            status_val = 1
        else:
            status_val = 0

        update_query = """
            UPDATE project_master SET
                project_name=%s, client_code=%s, category=%s, project_type_code=%s, num_users=%s,
                effective_from=%s, effective_to=%s, project_description=%s, 
                database_type_code=%s, front_end_tech_stack_code=%s, back_end_tech_stack_code=%s, status=%s
            WHERE project_code=%s
        """
        execute_query(update_query, (
            data.project_name, data.client_code, category_val, data.project_type_code, data.num_users,
            data.effective_from, data.effective_to, data.project_description, 
            data.database_type_code, data.front_end_tech_stack_code, data.back_end_tech_stack_code,
            status_val, code
        ))

        return {"message": f"Project '{data.project_name}' updated successfully!", "code": code}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@router.delete("/{code}", summary="Delete project")
def delete_project(code: str):
    try:
        execute_query("DELETE FROM project_master WHERE project_code=%s", (code,))
        return {"message": f"Project '{code}' deleted successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")


# NEW: used by tickets page dropdown
@router.get("/projects_dropdown", summary="Projects dropdown")
def projects_dropdown():
    try:
        rows = execute_query(
            "SELECT project_code AS code, project_name AS name FROM project_master ORDER BY project_name",
            fetch=True,
        )
        return rows
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading projects dropdown: {str(e)}")

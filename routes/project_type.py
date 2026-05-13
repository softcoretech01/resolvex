from fastapi import APIRouter, HTTPException
from models.project_type import ProjectTypeCreate, ProjectTypeUpdate
from db import execute_query
from utils import next_code, format_status
import traceback

router = APIRouter(tags=["Project Type"])

CATEGORY_MAP = {0: "New", 1: "Support"}
CATEGORY_REVERSE_MAP = {"0": 0, "1": 1, 0: 0, 1: 1, "new": 0, "support": 1}

def convert_status(status_str):
    return 1 if str(status_str).strip().lower() == "active" else 0

@router.post("/", summary="Add a new project type")
def add_project_type(data: ProjectTypeCreate):
    try:
        if not data.project_type_name or data.status is None:
            raise HTTPException(status_code=400, detail="Project Type Name and Status are required!")

        category_val = CATEGORY_REVERSE_MAP.get(data.category)
        if category_val is None:
            raise HTTPException(status_code=400, detail="Invalid category value!")

        status_val = convert_status(data.status)
        code = next_code("project_type_master", "PT", "project_type_id")

        execute_query(
            """
            INSERT INTO project_type_master 
            (project_type_code, project_type_name, category, description, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (code, data.project_type_name, category_val, data.description, status_val)
        )
        return {"message": f"Project Type '{data.project_type_name}' added successfully!", "code": code}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error saving project type")

@router.get("/", summary="Get all project types")
def get_project_types():
    try:
        rows = execute_query(
            "SELECT project_type_code, project_type_name, category, description, status FROM project_type_master",
            fetch=True
        )
        for row in rows:
            row['category'] = CATEGORY_MAP.get(row['category'], "Unknown")
        return format_status(rows)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error loading project types")

@router.put("/{code}", summary="Update a project type")
def update_project_type(code: str, data: ProjectTypeUpdate):
    try:
        if not data.project_type_name or data.status is None:
            raise HTTPException(status_code=400, detail="Project Type Name and Status are required!")

        category_val = CATEGORY_REVERSE_MAP.get(data.category)
        if category_val is None:
            raise HTTPException(status_code=400, detail="Invalid category value!")

        status_val = convert_status(data.status)

        execute_query(
            """
            UPDATE project_type_master 
            SET project_type_name=%s, category=%s, description=%s, status=%s 
            WHERE project_type_code=%s
            """,
            (data.project_type_name, category_val, data.description, status_val, code)
        )
        return {"message": f"Project Type '{data.project_type_name}' updated successfully!"}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error updating project type")

@router.delete("/{code}", summary="Delete a project type")
def delete_project_type(code: str):
    try:
        execute_query("DELETE FROM project_type_master WHERE project_type_code=%s", (code,))
        return {"message": f"Project Type '{code}' deleted successfully!"}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error deleting project type")

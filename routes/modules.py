from fastapi import APIRouter, HTTPException
from models.modules import ModuleCreate, ModuleUpdate
from db import execute_query
from utils import next_code
import traceback

router = APIRouter(tags=["Modules"])

@router.post("/", summary="Add a new module")
def add_module(data: ModuleCreate):
    try:
        # Validate required fields
        if not data.module_name or not data.module_type_code or not data.project_code or data.status is None:
            raise HTTPException(status_code=400, detail="Module Name, Module Type, Project, and Status are required!")
        status_val = 1 if data.status.lower() == "active" else 0
        code = next_code("modules", "MD", "module_id")

        execute_query(
            """
            INSERT INTO modules (module_code, module_name, module_type_code, project_code, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (code, data.module_name, data.module_type_code, data.project_code, status_val)
        )

        return {"message": f"Module '{data.module_name}' added successfully!", "module_code": code}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", summary="Get all modules")
def get_modules():
    try:
        query = """
            SELECT 
                m.module_id,
                m.module_code,
                m.module_name,
                m.module_type_code,
                mt.module_type_name,
                m.project_code,
                p.project_name,
                m.status,
                m.created_at,
                m.updated_at
            FROM modules m
            LEFT JOIN project_master p ON m.project_code = p.project_code
            LEFT JOIN module_type_master mt ON m.module_type_code = mt.module_type_code
        """
        rows = execute_query(query, fetch=True)
        for r in rows:
            r["status"] = "Active" if r["status"] == 1 else "Inactive"
        return rows
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{code}", summary="Update a module")
def update_module(code: str, data: ModuleUpdate):
    try:
        status_val = 1 if data.status.lower() == "active" else 0
        execute_query(
            """
            UPDATE modules SET module_name=%s, module_type_code=%s, project_code=%s, status=%s, updated_at=CURRENT_TIMESTAMP
            WHERE module_code=%s
            """,
            (data.module_name, data.module_type_code, data.project_code, status_val, code)
        )
        return {"message": f"Module '{data.module_name}' updated successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{code}", summary="Delete a module")
def delete_module(code: str):
    try:
        execute_query("DELETE FROM modules WHERE module_code=%s", (code,))
        return {"message": f"Module '{code}' deleted successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

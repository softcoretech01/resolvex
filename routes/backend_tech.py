from fastapi import APIRouter, HTTPException
from models.backend_tech import BackendTechCreate, BackendTechUpdate
from db import execute_query
from utils import next_code, format_status
import traceback

router = APIRouter()

@router.get("", summary="Get all module types")
@router.post("/", summary="Add a new backend tech stack")
def add_backend_tech_stack(data: BackendTechCreate):
    try:
        if not data.tech_stack_name or data.status is None:
            raise HTTPException(status_code=400, detail="Tech Stack Name and Status are required!")

        status_val = 1 if data.status.lower() == "active" else 0

        # Correct primary key column name as per DB schema
        code = next_code("backend_tech_stack_master", "TS", "back_end_tech_stack_id")

        execute_query(
            """
            INSERT INTO backend_tech_stack_master 
            (tech_stack_code, tech_stack_name, description, status) 
            VALUES (%s, %s, %s, %s)
            """,
            (code, data.tech_stack_name, data.description, status_val)
        )
        return {"message": f"Back End Tech Stack '{data.tech_stack_name}' added successfully!", "code": code}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving backend tech stack: {str(e)}")

@router.get("", summary="Get all backend tech stacks")
@router.get("/", summary="Get all backend tech stacks")
def get_backend_tech_stacks():
    try:
        rows = execute_query(
            "SELECT tech_stack_code, tech_stack_name, description, status FROM backend_tech_stack_master",
            fetch=True
        )
        return format_status(rows)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading backend tech stacks: {str(e)}")


@router.put("/{code}", summary="Update a backend tech stack")
def update_backend_tech_stack(code: str, data: BackendTechUpdate):
    try:
        if not data.tech_stack_name or data.status is None:
            raise HTTPException(status_code=400, detail="Tech Stack Name and Status are required!")

        status_val = 1 if data.status.lower() == "active" else 0

        execute_query(
            """
            UPDATE backend_tech_stack_master 
            SET tech_stack_name = %s, description = %s, status = %s 
            WHERE tech_stack_code = %s
            """,
            (data.tech_stack_name, data.description, status_val, code)
        )
        return {"message": f"Back End Tech Stack '{data.tech_stack_name}' updated successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating backend tech stack: {str(e)}")


@router.delete("/{code}", summary="Delete a backend tech stack")
def delete_backend_tech_stack(code: str):
    try:
        execute_query("DELETE FROM backend_tech_stack_master WHERE tech_stack_code = %s", (code,))
        return {"message": f"Back End Tech Stack '{code}' deleted successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting backend tech stack: {str(e)}")

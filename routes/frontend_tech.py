from fastapi import APIRouter, HTTPException
from models.frontend_tech import FrontendTechCreate, FrontendTechUpdate
from db import execute_query
from utils import next_code, format_status
import traceback

router = APIRouter()

@router.post("/", summary="Add a new frontend tech stack")
def add_frontend_tech_stack(data: FrontendTechCreate):
    try:
        if not data.tech_stack_name or data.status is None:
            raise HTTPException(status_code=400, detail="Tech Stack Name and Status are required!")

        status_val = 1 if data.status.lower() == "active" else 0

        # Use table's correct PK column for code generation
        code = next_code("frontend_tech_stack_master", "FE", "front_end_tech_stack_id")

        execute_query(
            """
            INSERT INTO frontend_tech_stack_master
            (front_end_tech_stack_code, front_end_tech_stack_name, description, status)
            VALUES (%s, %s, %s, %s)
            """,
            (code, data.tech_stack_name, data.description, status_val)
        )
        return {"message": f"Frontend Tech Stack '{data.tech_stack_name}' added successfully!", "code": code}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving frontend tech stack: {str(e)}")

@router.get("/", summary="Get all frontend tech stacks")
def get_frontend_tech_stacks():
    try:
        rows = execute_query(
            """
            SELECT 
                front_end_tech_stack_code AS tech_stack_code,
                front_end_tech_stack_name AS tech_stack_name,
                description,
                status
            FROM frontend_tech_stack_master
            """,
            fetch=True
        )
        return format_status(rows)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading frontend tech stacks: {str(e)}")

@router.put("/{code}", summary="Update a frontend tech stack")
def update_frontend_tech_stack(code: str, data: FrontendTechUpdate):
    try:
        if not data.tech_stack_name or data.status is None:
            raise HTTPException(status_code=400, detail="Tech Stack Name and Status are required!")

        status_val = 1 if data.status.lower() == "active" else 0

        execute_query(
            """
            UPDATE frontend_tech_stack_master
            SET front_end_tech_stack_name = %s, description = %s, status = %s
            WHERE front_end_tech_stack_code = %s
            """,
            (data.tech_stack_name, data.description, status_val, code)
        )
        return {"message": f"Frontend Tech Stack '{data.tech_stack_name}' updated successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating frontend tech stack: {str(e)}")

@router.delete("/{code}", summary="Delete a frontend tech stack")
def delete_frontend_tech_stack(code: str):
    try:
        execute_query(
            "DELETE FROM frontend_tech_stack_master WHERE front_end_tech_stack_code = %s", (code,)
        )
        return {"message": f"Frontend Tech Stack '{code}' deleted successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting frontend tech stack: {str(e)}")

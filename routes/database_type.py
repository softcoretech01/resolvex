from fastapi import APIRouter, HTTPException
from models.database_type import DatabaseTypeCreate, DatabaseTypeUpdate
from db import execute_query
from utils import next_code, format_status
import traceback

router = APIRouter()

@router.post("/", summary="Add a new database type")
def add_database_type(data: DatabaseTypeCreate):
    try:
        if not data.database_type_name or data.status is None:
            raise HTTPException(status_code=400, detail="Database Type Name and Status are required!")

        status_val = 1 if data.status.lower() == "active" else 0
        code = next_code("database_type_master", "DB", "database_type_id")

        execute_query(
            """
            INSERT INTO database_type_master
            (database_type_code, database_type_name, description, status)
            VALUES (%s, %s, %s, %s)
            """,
            (code, data.database_type_name, data.description, status_val)
        )

        return {"message": f"Database Type '{data.database_type_name}' added successfully!", "code": code}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving database type: {str(e)}")

@router.get("/", summary="Get all database types")
def get_database_types():
    try:
        rows = execute_query(
            """
            SELECT 
                database_type_code AS database_type_code,
                database_type_name AS database_type_name,
                description, status
            FROM database_type_master
            """,
            fetch=True
        )
        return format_status(rows)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading database types: {str(e)}")

@router.put("/{code}", summary="Update a database type")
def update_database_type(code: str, data: DatabaseTypeUpdate):
    try:
        if not data.database_type_name or data.status is None:
            raise HTTPException(status_code=400, detail="Database Type Name and Status are required!")

        status_val = 1 if data.status.lower() == "active" else 0
        execute_query(
            """
            UPDATE database_type_master
            SET database_type_name = %s, description = %s, status = %s
            WHERE database_type_code = %s
            """,
            (data.database_type_name, data.description, status_val, code)
        )

        return {"message": f"Database Type '{data.database_type_name}' updated successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating database type: {str(e)}")

@router.delete("/{code}", summary="Delete a database type")
def delete_database_type(code: str):
    try:
        execute_query(
            "DELETE FROM database_type_master WHERE database_type_code = %s", (code,)
        )
        return {"message": f"Database Type '{code}' deleted successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting database type: {str(e)}")

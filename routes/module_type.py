from fastapi import APIRouter, HTTPException
from models.module_type import ModuleTypeCreate, ModuleTypeUpdate
from db import execute_query
from utils import next_code, format_status
import traceback

router = APIRouter(tags=["Module Type"])

@router.post("", summary="Add a new module type")
@router.post("/", summary="Add a new module type")
def add_module_type(data: ModuleTypeCreate):
    try:
        if not data.module_type_name or data.status is None:
            raise HTTPException(status_code=400, detail="Module Type Name and Status are required!")

        # Handle status as string/int robustly
        status_val = 1 if str(data.status).lower() == "active" or str(data.status) == "1" else 0
        code = next_code("module_type_master", "MT", "module_type_id")

        execute_query(
            """
            INSERT INTO module_type_master 
            (module_type_code, module_type_name, description, status) 
            VALUES (%s, %s, %s, %s)
            """,
            (code, data.module_type_name, data.description, status_val)
        )
        return {"message": f"Module Type '{data.module_type_name}' added successfully!", "code": code}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving module type: {str(e)}")

@router.get("", summary="Get all module types")
@router.get("/", summary="Get all module types")
def get_module_types():
    try:
        rows = execute_query(
            """
            SELECT module_type_code, module_type_name, description, status 
            FROM module_type_master
            """,
            fetch=True
        )
        return format_status(rows)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading module types: {str(e)}")

@router.get("/{code}", summary="Get module type by code")
def get_module_type(code: str):
    try:
        rows = execute_query(
            """
            SELECT module_type_code, module_type_name, description, status 
            FROM module_type_master 
            WHERE module_type_code=%s
            """,
            (code,), fetch=True
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Module Type not found")
        return format_status(rows)[0]
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading module type: {str(e)}")

@router.put("/{code}", summary="Update a module type")
def update_module_type(code: str, data: ModuleTypeUpdate):
    try:
        if not data.module_type_name or data.status is None:
            raise HTTPException(status_code=400, detail="Module Type Name and Status are required!")

        status_val = 1 if str(data.status).lower() == "active" or str(data.status) == "1" else 0
        execute_query(
            """
            UPDATE module_type_master 
            SET module_type_name=%s, description=%s, status=%s 
            WHERE module_type_code=%s
            """,
            (data.module_type_name, data.description, status_val, code)
        )
        return {"message": f"Module Type '{data.module_type_name}' updated successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating module type: {str(e)}")

@router.delete("/{code}", summary="Delete a module type")
def delete_module_type(code: str):
    try:
        execute_query(
            "DELETE FROM module_type_master WHERE module_type_code=%s",
            (code,)
        )
        return {"message": f"Module Type '{code}' deleted successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting module type: {str(e)}")

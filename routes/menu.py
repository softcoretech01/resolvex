from fastapi import APIRouter, HTTPException, Query
from models.menu import MenuCreate, MenuUpdate
from db import execute_query
from utils import next_code, format_status
import traceback

router = APIRouter(tags=["menus"])

# ----------------------------------------------
# 1. FETCH MENUS FOR DROPDOWNS (USED IN MULTIPLE UIs)
# ----------------------------------------------
@router.get("/menus", summary="Get menus (optionally filter by module_code)")
def get_dropdown_menus(module_code: str = Query(None)):
    try:
        query = "SELECT menu_code, menu_name FROM menu_master"
        params = ()

        if module_code:
            query += " WHERE module_code = %s AND status = 1"
            params = (module_code,)

        query += " ORDER BY menu_name"

        rows = execute_query(query, params, fetch=True)
        return rows

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching menus: {str(e)}")

# ----------------------------------------------
# 2. FETCH MENUS BY MODULE + PROJECT (Project Users Page)
# ----------------------------------------------
@router.get("/by-module", summary="Get menus filtered by module_code + project_code")
def get_menus_by_module(project_code: str, module_code: str):
    try:
        rows = execute_query(
            """
            SELECT menu_code, menu_name 
            FROM menu_master
            WHERE project_code = %s 
              AND module_code = %s
              AND status = 1
            ORDER BY menu_name
            """,
            (project_code, module_code),
            fetch=True
        )
        return rows

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching menus: {str(e)}")

# ----------------------------------------------
# 3. FETCH ALL MENUS (FULL TABLE LISTING)
# ----------------------------------------------
@router.get("", summary="Get all menus")
@router.get("/", summary="Get all menus")
def get_menus():
    try:
        rows = execute_query(
            """
            SELECT 
                m.menu_code, 
                m.menu_name, 
                mo.module_name AS module_text, 
                p.project_name AS project_text,
                m.project_code,
                m.status, 
                m.created_at, 
                m.updated_at
            FROM menu_master m
            LEFT JOIN modules mo ON m.module_code = mo.module_code
            LEFT JOIN project_master p ON m.project_code = p.project_code
            ORDER BY m.menu_id DESC
            """,
            fetch=True
        )
        return format_status(rows)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching menus: {str(e)}")

# ----------------------------------------------
# 4. CREATE NEW MENU
# ----------------------------------------------
@router.post("", summary="Add a new menu")
@router.post("/", summary="Add a new menu")
def add_menu(data: MenuCreate):
    try:
        if not data.menu_name or not data.module_code or not data.project_code:
            raise HTTPException(status_code=400, detail="Menu Name, Module, and Project are required!")

        # Validate module
        module_exists = execute_query(
            "SELECT COUNT(*) AS cnt FROM modules WHERE module_code=%s AND status=1",
            (data.module_code,),
            fetch=True
        )
        if not module_exists or module_exists[0]["cnt"] == 0:
            raise HTTPException(status_code=400, detail="Selected module does not exist or is inactive!")

        # Generate next menu code
        code = next_code("menu_master", "MN", "menu_id")

        execute_query(
            """
            INSERT INTO menu_master (menu_code, menu_name, module_code, project_code, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (code, data.menu_name, data.module_code, data.project_code, data.status)
        )

        return {"message": f"Menu '{data.menu_name}' added successfully!", "code": code}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error adding menu: {str(e)}")

# ----------------------------------------------
# 5. UPDATE MENU
# ----------------------------------------------
@router.put("/{code}", summary="Update an existing menu")
def update_menu(code: str, data: MenuUpdate):
    try:
        exists = execute_query(
            "SELECT COUNT(*) AS cnt FROM menu_master WHERE menu_code=%s",
            (code,),
            fetch=True
        )
        if not exists or exists[0]["cnt"] == 0:
            raise HTTPException(status_code=404, detail=f"Menu with code '{code}' not found!")

        # Validate module if updated
        if data.module_code is not None:
            module_exists = execute_query(
                "SELECT COUNT(*) AS cnt FROM modules WHERE module_code=%s AND status=1",
                (data.module_code,),
                fetch=True
            )
            if not module_exists or module_exists[0]["cnt"] == 0:
                raise HTTPException(status_code=400, detail="Selected module does not exist or is inactive!")

        execute_query(
            """
            UPDATE menu_master
            SET menu_name=%s, module_code=%s, project_code=%s, status=%s, updated_at=NOW()
            WHERE menu_code=%s
            """,
            (data.menu_name, data.module_code, data.project_code, data.status, code)
        )

        return {"message": f"Menu '{code}' updated successfully!"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating menu: {str(e)}")

# ----------------------------------------------
# 6. DELETE MENU
# ----------------------------------------------
@router.delete("/{code}", summary="Delete a menu")
def delete_menu(code: str):
    try:
        execute_query("DELETE FROM menu_master WHERE menu_code=%s", (code,))
        return {"message": f"Menu '{code}' deleted successfully!"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting menu: {str(e)}")

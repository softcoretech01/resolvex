from fastapi import APIRouter, HTTPException
from models.client import ClientCreate, ClientUpdate
from db import execute_query
from utils import next_code, format_status
import traceback

router = APIRouter(tags=["Client"])

@router.post("/", summary="Add a new client")
def add_client(data: ClientCreate):
    try:
        if not data.client_name or not data.country or data.status is None:
            raise HTTPException(status_code=400, detail="Client Name, Country, and Status are required!")

        status_val = 1 if str(data.status).lower() == "active" else 0
        code = next_code("client_master", "CL", "client_id")

        execute_query(
            """
            INSERT INTO client_master 
            (client_code, client_name, country, state, city, address, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (code, data.client_name, data.country, data.state, data.city, data.address, status_val)
        )

        return {"message": f"Client '{data.client_name}' added successfully!", "code": code}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving client: {str(e)}")


@router.get("/", summary="Get all clients")
def get_clients():
    try:
        rows = execute_query(
            """
            SELECT 
                client_code, client_name, country, state, city, address, status 
            FROM client_master
            """,
            fetch=True
        )
        return format_status(rows)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading clients: {str(e)}")


@router.put("/{code}", summary="Update a client")
def update_client(code: str, data: ClientUpdate):
    try:
        if not data.client_name or not data.country or data.status is None:
            raise HTTPException(status_code=400, detail="Client Name, Country, and Status are required!")

        status_val = 1 if str(data.status).lower() == "active" else 0

        execute_query(
            """
            UPDATE client_master 
            SET client_name = %s, country = %s, state = %s, city = %s, address = %s, status = %s 
            WHERE client_code = %s
            """,
            (data.client_name, data.country, data.state, data.city, data.address, status_val, code)
        )

        return {"message": f"Client '{data.client_name}' updated successfully!"}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating client: {str(e)}")


@router.delete("/{code}", summary="Delete a client")
def delete_client(code: str):
    try:
        execute_query(
            "DELETE FROM client_master WHERE client_code = %s",
            (code,)
        )
        return {"message": f"Client '{code}' deleted successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting client: {str(e)}")

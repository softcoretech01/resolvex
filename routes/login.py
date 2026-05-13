from fastapi import APIRouter, HTTPException
from models.login import LoginCredentials, LoginResponse, UserRegistration
from db import execute_query
import traceback

router = APIRouter(tags=["Authentication"])


# -------------------------------------------------
# LOGIN
# -------------------------------------------------
@router.post("/login", response_model=LoginResponse, summary="User Login")
def user_login(data: LoginCredentials):
    """
    Authenticates a user using email (user_name) and password
    """
    try:
        query = """
            SELECT project_user_name, user_role, password
            FROM users
            WHERE user_name = %s
        """
        rows = execute_query(query, (data.user_name,), fetch=True)

        if not rows:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        user = rows[0]

        # ⚠ Plaintext password comparison (OK for dev, NOT for prod)
        if user["password"] != data.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return LoginResponse(
            user_name=user["project_user_name"],
            role=user["user_role"]
        )

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Login failed")


# -------------------------------------------------
# REGISTER
# -------------------------------------------------
@router.post("/register", summary="Register New User")
def register_user(data: UserRegistration):
    """
    Registers a user.
    project_user_id is AUTO_INCREMENT (DO NOT INSERT IT)
    """
    try:
        # Check if email already exists
        check_query = "SELECT 1 FROM users WHERE user_name = %s"
        exists = execute_query(check_query, (data.user_name,), fetch=True)

        if exists:
            raise HTTPException(status_code=409, detail="Email already registered")

        # ✅ INSERT (NO project_user_id here)
        insert_query = """
            INSERT INTO users
            (project_user_name, user_name, password, user_role)
            VALUES (%s, %s, %s, %s)
        """

        execute_query(
            insert_query,
            (
                data.project_user_name,
                data.user_name,
                data.password,   # ⚠ Hash in production
                data.user_role,
            )
        )

        return {
            "message": f"Account created successfully for {data.user_name}. Please login."
        }

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Registration failed")

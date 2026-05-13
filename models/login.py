from pydantic import BaseModel, Field
from typing import Optional

class LoginCredentials(BaseModel):
    """Schema for receiving user credentials (Username/Email and Password) during Sign In."""
    user_name: str = Field(..., description="Username (Email) for login")
    password: str = Field(..., description="Password for login")

class LoginResponse(BaseModel):
    """Schema for sending back successful login information."""
    user_name: str = Field(..., description="The authenticated user's display name (project_user_name)")
    role: str = Field(..., description="The verified role (e.g., L4_ADMIN)")
    message: str = Field(default="Login successful", description="Status or info message")

class UserRegistration(BaseModel):
    """Schema for receiving registration data during Sign Up."""
    project_user_name: str = Field(..., description="Full display name of the user")
    user_name: str = Field(..., description="Login username (Email)")
    password: str = Field(..., description="Password")
    user_role: str = Field(..., description="Assigned role (e.g., L1_HELPDESK)")

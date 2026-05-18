from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class ProjectUserBase(BaseModel):
    project_code: str = Field(..., description="Project code from project_master")
    project_user_name: str = Field(..., max_length=50, description="Name of the project user")
    email: EmailStr = Field(..., description="Email of the project user")
    module_code: Optional[List[str]] = Field(default=None, description="List of selected module codes")
    menu_code: Optional[List[str]] = Field(default=None, description="List of selected menu codes")
    status: Optional[int] = Field(default=1, description="1 = Active, 0 = Inactive")

class ProjectUserCreate(ProjectUserBase):
    pass

class ProjectUserUpdate(BaseModel):
    project_code: Optional[str] = None
    project_user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    module_code: Optional[List[str]] = None
    menu_code: Optional[List[str]] = None
    status: Optional[int] = None

class ProjectUserResponse(ProjectUserBase):
    project_user_id: int
    project_name: Optional[str] = Field(None, description="Name of the project (from project_master)")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

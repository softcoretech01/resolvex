from pydantic import BaseModel
from typing import List, Optional

class ProjectBase(BaseModel):
    project_name: Optional[str] = None
    client_code: Optional[str] = None
    category: Optional[str] = None
    project_type_code: Optional[str] = None
    num_users: Optional[int] = 0
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    project_description: Optional[str] = ""
    database_type_code: Optional[str] = None
    front_end_tech_stack_code: Optional[str] = None
    back_end_tech_stack_code: Optional[str] = None
    status: Optional[str] = None

class ProjectCreate(ProjectBase):
    project_name: str
    client_code: str
    category: str
    project_type_code: str
    status: str

class ProjectUpdate(ProjectBase):
    pass

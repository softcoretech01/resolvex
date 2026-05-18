from pydantic import BaseModel
from typing import Optional

class ProjectTypeCreate(BaseModel):
    project_type_name: str
    category: str
    description: Optional[str] = None
    status: str

class ProjectTypeUpdate(BaseModel):
    project_type_name: str
    category: Optional[str] = None 
    description: Optional[str] = None
    status: str

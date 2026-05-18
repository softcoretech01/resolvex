from pydantic import BaseModel

class ModuleCreate(BaseModel):
    module_name: str
    module_type_code: str
    project_code: str  # Changed from project_id (int) to project_code (str)
    status: str

class ModuleUpdate(BaseModel):
    module_name: str
    module_type_code: str
    project_code: str  # Changed from project_id (int) to project_code (str)
    status: str

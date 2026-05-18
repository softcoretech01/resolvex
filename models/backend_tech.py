from pydantic import BaseModel
from typing import Optional

class BackendTechCreate(BaseModel):
    tech_stack_name: str
    description: Optional[str] = None
    status: str  
class BackendTechUpdate(BaseModel):
    tech_stack_name: str
    description: Optional[str] = None
    status: str  

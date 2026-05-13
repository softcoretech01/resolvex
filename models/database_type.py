from pydantic import BaseModel
from typing import Optional

class DatabaseTypeCreate(BaseModel):
    database_type_name: str
    description: Optional[str] = ""
    status: str  

class DatabaseTypeUpdate(BaseModel):
    database_type_name: str
    description: Optional[str] = ""
    status: str  

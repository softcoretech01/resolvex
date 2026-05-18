from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MenuBase(BaseModel):
    menu_name: str
    menu_code: str
    module_code: str
    project_code: str       # string, matches your code-based DB schema
    status: int

class MenuCreate(BaseModel):
    menu_name: str
    module_code: str        # changed from module_name for consistency
    project_code: str       # changed from int to str
    status: int

class MenuUpdate(BaseModel):
    menu_name: Optional[str] = None
    menu_code: Optional[str] = None
    module_code: Optional[str] = None
    project_code: Optional[str] = None
    status: Optional[int] = None

class MenuOut(MenuBase):
    menu_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

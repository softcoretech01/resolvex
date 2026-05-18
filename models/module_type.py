from pydantic import BaseModel

class ModuleTypeBase(BaseModel):
    module_type_name: str
    description: str | None = None
    status: str  

class ModuleTypeCreate(ModuleTypeBase):
    pass

class ModuleTypeUpdate(ModuleTypeBase):
    pass

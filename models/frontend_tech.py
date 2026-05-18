from pydantic import BaseModel

class FrontendTechCreate(BaseModel):
    tech_stack_name: str
    description: str = None
    status: str

class FrontendTechUpdate(BaseModel):
    tech_stack_name: str
    description: str = None
    status: str

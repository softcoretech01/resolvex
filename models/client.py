from pydantic import BaseModel
from typing import Optional

class ClientCreate(BaseModel):
    client_name: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    status: str 

class ClientUpdate(BaseModel):
    client_name: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    status: str  

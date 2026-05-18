from pydantic import BaseModel
from typing import Optional
from datetime import date, time


class TicketBase(BaseModel):
    # Codes (FKs)
    project_code: Optional[str] = None
    module_type_code: Optional[str] = None
    module_code: Optional[str] = None
    

    # Issue
    issue_short: Optional[str] = None
    issue_desc: Optional[str] = None

    # Reporter (client)
    reported_user_code: Optional[str] = None
    reported_date: Optional[date] = None
    reported_time: Optional[time] = None

    # Priority / severity
    priority: Optional[str] = None
    severity: Optional[str] = None

    # Users affected by the issue
    affected_user: Optional[str] = None

    # Target / assignee (project user)
    target_date: Optional[date] = None
    assigned_to_code: Optional[str] = None

    status: Optional[str] = None
    environment: Optional[str] = None
    sql_script: Optional[str] = None
    sql_attachment: Optional[str] = None
    short_name: Optional[str] = None


class TicketCreate(TicketBase):
    project_code: str
    module_type_code: str
    module_code: str
    

    issue_short: str
    reported_user_code: str

    priority: str
    severity: str
    # affected_user will be filled optionally


class TicketUpdate(TicketBase):
    pass

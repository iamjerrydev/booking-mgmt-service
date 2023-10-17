from pydantic import BaseModel
from typing import Optional, Literal

TASK_STATUS_VALUES = Literal[
    'To Do', 
    'Approved',
    'In Progress', 
    'Done', 
    'Cancelled'
    ]

class TaskModel(BaseModel):
    booking_id: str
    booking_ref: str
    shop_id: str
    status: TASK_STATUS_VALUES = 'To Do'
    start_datetime: str
    end_datetime: str
    service_id: str
    assignee_id: str

class PutTaskModel(BaseModel):
    status: Optional[TASK_STATUS_VALUES] = 'Tentative'
    start_datetime: Optional[str] =  None
    end_datetime: Optional[str] =  None
    service_id: Optional[str] = None
    assignee_id: Optional[str] = None
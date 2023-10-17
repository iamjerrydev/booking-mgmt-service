from pydantic import BaseModel
from typing import Optional


class AssigneeModel(BaseModel):
    name: str
    role: Optional[str] = None
    photo_url: Optional[str] = None
    services: Optional[list] = []
    accept_booking: Optional[bool] = True
    availability: Optional[dict] = {
        'Sunday': [],
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
        'Saturday': [],
    }
    leaves: Optional[list] = []


class PutAssigneeModel(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    photo_url: Optional[str] = None
    services: Optional[list] = []
    accept_booking: Optional[bool] = True
    availability: Optional[dict] = {}
    leaves: Optional[list] = []
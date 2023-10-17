from pydantic import BaseModel
from typing import Optional


class ServiceModel(BaseModel):
    title: str
    duration: int
    amount: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    assignees: Optional[list] = []
    is_active: bool = True
    remarks: Optional[str] = None


class PutServiceModel(BaseModel):
    title: Optional[str] = None
    duration: Optional[int] = 0
    amount: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    assignees: Optional[list] = []
    is_active: Optional[bool] = True
    remarks: Optional[str] = None
from pydantic import BaseModel
from typing import Optional, Literal

BOOKING_STATUS_VALUES = Literal[
    'Tentative', 
    'Confirmed', 
    'Completed', 
    'Declined', 
    'No Show'
    ]

class BookingModel(BaseModel):
    status: BOOKING_STATUS_VALUES = 'Tentative'
    shop_id: str
    tasks: list
    customer: dict
    additional_fields: Optional[dict] = {}
    remarks: Optional[str] = None

class PutBookingModel(BaseModel):
    customer: Optional[dict] = {}
    additional_fields: Optional[dict] = {}
    remarks: Optional[str] = None
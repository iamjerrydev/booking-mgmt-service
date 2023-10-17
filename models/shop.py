from pydantic import BaseModel
from typing import Optional, Literal


class ShopModel(BaseModel):
    shop_id: str
    name: str
    is_active: Optional[bool] = True
    slug: Optional[str] = None
    logo: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    operating_hours: dict = {
        "Monday": [],
        "Thursday": [],
        "Friday": [],
        "Sunday": [],
        "Wednesday": [],
        "Tuesday": [],
        "Saturday": []
    }

class PutShopModel(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = True
    logo: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    operating_hours: Optional[dict] = {
        "Monday": [],
        "Thursday": [],
        "Friday": [],
        "Sunday": [],
        "Wednesday": [],
        "Tuesday": [],
        "Saturday": []
    }

default_questionnaires = [
    {
        "field": "Customer Name",
        "label": "Full Name",
        "type": "text",
        "options": "",
        "code": "name",
        "is_required": True,
        "is_editable": False
    },
    {
        "field": "Mobile Number",
        "label": "Phone Number",
        "type": "mobile_number",
        "options": "",
        "code": "mobile_no",
        "is_required": True,
        "is_editable": False
    },
    {
        "field": "Email Address",
        "label": "Email Address",
        "type": "email",
        "options": "",
        "code": "email_address",
        "is_required": True,
        "is_editable": False
    }
]

default_confirmation_message = "Hello {name}! \nCongratulations! We have received your booking request. Please keep your line open for the confirmation. Our receptionist will reach out to you through your mobile number ({mobile_number}). \nSee you soon!"

class ShopSettingModel(BaseModel):
    slot_availability: Literal['assignee_availability', 'store_availability'] = 'assignee_availability'
    allowed_days_for_advanced_booking: int = 14
    min_booking_notice: int = 2
    questionnaires: Optional[list] = default_questionnaires
    confirmation_message: Optional[str] = default_confirmation_message
    auto_confirm_booking: bool = False
    email_notifications: Optional[list] = []
    sms_notifications: Optional[list] = []
    allow_assignee_selection: bool = False
    assignee_handle: str = 'staff'
    allow_multiple_service_selection: bool = True

class PutShopSettingModel(BaseModel):
    slot_availability: Literal['assignee_availability', 'store_availability'] = 'assignee_availability'
    allowed_days_for_advanced_booking: int = 14
    min_booking_notice: int = 2
    confirmation_message: Optional[str] = default_confirmation_message
    auto_confirm_booking: bool = False
    allow_assignee_selection: bool = False
    assignee_handle: str = 'staff'
    allow_multiple_service_selection: bool = True
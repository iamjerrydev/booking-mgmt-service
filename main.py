import logging

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware

from mangum import Mangum
from dotenv import load_dotenv

from endpoints import *
from models import *

load_dotenv()

app = FastAPI()
handler = Mangum(app)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTH

@app.post("/verify-user")
async def api_verify_user(user_request: UserModel):
    logging.info("Verifying User {}".format(user_request.username))
    user_token = method_verify_user(user_request.username, user_request.password)
    logging.info("User {} has logged in successfully".format(user_request.username))
    return user_token 

# SHOP ENDPOINTS

@app.post("/create-shop", status_code=status.HTTP_201_CREATED)
async def api_create_shop(shop_request: ShopModel):
    logging.info("Creating Shop for {}".format(shop_request.name))
    shop = method_create_shop(shop_request)
    logging.info("Shop Details: {}".format(shop))
    return shop 

@app.get("/get-shop")
async def api_get_shop_details(request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get Shop Details: {}".format(shop_id))
    shop = method_get_shop_by_id(shop_id=shop_id)
    logging.info("Shop Details: {}".format(shop))
    return shop
    
@app.put("/update-shop")
async def update_shop(shop_request: PutShopModel, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    updated_shop_data = reconstruct_updated_data(
        old_fields=method_get_shop_by_id(shop_id=shop_id),
        model=PutShopModel,
        new_fields=shop_request.model_dump(exclude_unset=True)
    )
    updated_shop = method_update_shop(shop_id, updated_shop_data)
    logging.info("Updated Shop: {}".format(updated_shop))
    return updated_shop 

@app.get("/get-shop-setting")
async def api_get_shop_setting(request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get Shop Setting: {}".format(shop_id))
    shop_setting = method_get_shop_setting_by_id(shop_id=shop_id)
    logging.info("Shop Setting: {}".format(shop_setting))
    return shop_setting 

@app.put("/update-shop-setting")
async def update_shop_settings(shop_setting_request: ShopSettingModel, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    updated_shop_setting = reconstruct_updated_data(
        old_fields=method_get_shop_by_id(shop_id=shop_id),
        model=ShopSettingModel,
        new_fields=shop_setting_request.model_dump(exclude_unset=True)
    )
    shop_setting = method_update_shop_settings(shop_id, updated_shop_setting)
    logging.info("Updated Shop Setting: {}".format(shop_setting))
    return shop_setting 

# BOOKING ENDPOINTS

@app.post("/create-booking", status_code=status.HTTP_201_CREATED)
async def api_create_booking(booking_request: BookingModel, request: Request):
    if request.headers.get('x-client') != 'client-app':
        validate_user(token=request.headers.get('Authorization'))
    logging.info("Creating Booking for {}".format(booking_request.customer['name']))
    booking = method_create_booking(booking_request)
    logging.info("Booking Details: {}".format(booking))
    return booking

@app.get("/get-booking-by-id")
async def get_booking_by_id(booking_id: str, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get Booking: {}".format(booking_id))
    booking = method_get_booking_by_id(
        shop_id=shop_id, 
        booking_id=booking_id)
    logging.info("Booking: {}".format(booking_id))
    return booking 

@app.get("/get-booking-by-ref")
async def get_booking_by_ref(booking_ref: str, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    booking_ref = booking_ref.upper()
    logging.info("Get Booking: {}".format(booking_ref))
    booking = method_get_booking_by_ref(
        shop_id=shop_id, 
        booking_ref=booking_ref)
    logging.info("Booking: {}".format(booking_ref))
    return booking 

@app.get("/get-bookings-by-date")
async def get_bookings_by_date(start_date: str, duration: int, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get All Bookings on {0} + {1} days".format(start_date, duration))
    bookings = method_get_bookings_by_date(
        shop_id=shop_id, 
        start_date=start_date,
        end_date=add_date(start_date, duration)
        )
    logging.info("Bookings on {0} + {1} days".format(start_date, duration))
    return bookings 

@app.get("/get-bookings-by-status")
async def get_bookings_by_status(start_date: str, duration: int, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get Booking by Status")
    bookings = method_get_bookings_by_status(
        shop_id=shop_id, 
        start_date=start_date, 
        end_date=add_date(start_date, duration)
        )
    logging.info("Bookings by status")
    return bookings 

@app.get("/get-available-slots")
async def get_available_slots(booking_date, duration, assignee_id=None, request:Request=None):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get available slots for {}".format(assignee_id))
    available_slots = method_get_available_slots(
        shop_id=shop_id, 
        booking_date=booking_date,
        duration=int(duration),
        assignee_id=assignee_id,
        excluded_slots=None
        )
    return available_slots 

@app.put("/update-booking-status")
async def update_booking(booking_id: str, status: str, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    if status not in BOOKING_STATUS_VALUES.__args__:
        logging.info("Invalid Value for Booking Status: {}".format(status))
        raise HTTPException(status_code=400, 
                            detail="Invalid Value for Booking Status: {}".format(status))
    updated_booking = method_update_booking_status(shop_id, booking_id, status)
    return updated_booking

@app.put("/update-booking")
async def update_booking(booking_id: str, booking_request: PutBookingModel, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    current_val = method_get_booking_by_id(shop_id=shop_id, booking_id=booking_id, include_tasks=False)
    new_fields = booking_request.model_dump(exclude_unset=True)
    updated_booking_data = reconstruct_updated_data(
        old_fields=current_val,
        model=PutBookingModel,
        new_fields=new_fields
    )
    updated_booking_data['updated_at'] = get_current_time()
    updated_booking = method_update_booking(booking_id, updated_booking_data)
    return updated_booking

# TASK ENDPOINTS

@app.post("/create-task", status_code=status.HTTP_201_CREATED)
async def api_create_task(task_request: TaskModel, request: Request):
    validate_user(token=request.headers.get('Authorization'))
    logging.info("Creating Task for {}".format(task_request.booking_id))
    task = method_create_task(task_request)
    logging.info("Task Details: {}".format(task))
    return task

@app.get("/get-tasks-by-date")
async def get_tasks_by_date(date_str: str, request: Request, include_all:bool=False):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get All Tasks on {0}".format(date_str))
    tasks = method_get_tasks_by_date(
        shop_id=shop_id, 
        date_str=date_str,
        include_all=include_all
        )
    logging.info("Tasks on {0}".format(date_str))
    return tasks 

@app.get("/get-tasks-by-assignee")
async def get_tasks_by_assignee(assignee_id: str, start_date: str, duration: int, request: Request, include_all:bool=False):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get All Tasks for {}".format(assignee_id))
    tasks = method_get_tasks_by_assignee(
        shop_id=shop_id, 
        assignee_id=assignee_id, 
        start_date=start_date, 
        end_date=add_date(start_date, duration),
        include_all=include_all
        )
    logging.info("Tasks for {}".format(assignee_id))
    return tasks 

@app.put("/update-task")
async def update_task(booking_id: str, task_id: str, task_request: PutTaskModel, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    current_val = db_get_task_by_id(booking_id, task_id)
    new_fields = task_request.model_dump(exclude_unset=True)
    updated_task_data = reconstruct_updated_data(
        old_fields=current_val,
        model=PutTaskModel,
        new_fields=new_fields
    )
    if new_fields.get('status'):
        if task_request.status not in TASK_STATUS_VALUES.__args__:
            logging.info("Invalid Value for Task Status: {}".format(task_request.status))
            raise HTTPException(status_code=400, 
                                detail="Invalid Value for Task Status: {}".format(task_request.status))
    updated_task = method_update_task(shop_id, booking_id, task_id, updated_task_data)
    return updated_task

@app.delete("/delete-task")
async def api_delete_task(booking_id, task_id, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Deleting Task {}".format(task_id))
    method_delete_task(shop_id, booking_id, task_id)
    logging.info("Deleted Task: {}".format(task_id))
    return "{} deleted.".format(task_id)

# SERVICE ENDPOINTS

@app.post("/create-service", status_code=status.HTTP_201_CREATED)
async def create_service(service_request: ServiceModel, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Creating Service for {}".format(service_request.title))
    service = method_create_service(shop_id, service_request)
    logging.info("Service Details: {}".format(service))
    return service

@app.get("/get-service")
async def get_service(service_id: str, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get Service: {}".format(service_id))
    service = method_get_service_by_id(shop_id=shop_id, service_id=service_id)
    logging.info("Service: {}".format(service))
    return service 

@app.get("/get-services")
async def get_services(request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get Services for shop {}".format(shop_id))
    services = method_get_services(shop_id=shop_id)
    logging.info("Services: {}".format(services))
    return services 

@app.put("/update-service")
async def update_service(service_id: str, service_request: PutServiceModel, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    current_val = method_get_service_by_id(shop_id=shop_id, service_id=service_id)
    new_fields = service_request.model_dump(exclude_unset=True)

    current_assignees = current_val.pop('assignees')
    new_assignees = []

    if new_fields.get('assignees'):
        new_assignees = new_fields.pop('assignees')
        validate_assignees(shop_id=shop_id, assignee_ids=new_assignees)
    
    updated_service_data = reconstruct_updated_data(
        old_fields=current_val,
        model=PutServiceModel,
        new_fields=new_fields
    )
    
    updated_service_data.pop('assignees')
    updated_service = method_update_service(shop_id, service_id, updated_service_data)
    logging.info("Updated Service: {}".format(updated_service))

    if new_assignees:
        method_update_service_assignees(shop_id, current_assignees, new_assignees, updated_service)

    updated_service['assignees'] = method_get_assignees_by_service(service_id)

    return updated_service 

# ASSIGNEE ENDPOINTS

@app.post("/create-assignee", status_code=status.HTTP_201_CREATED)
async def create_assignee(assignee_request: AssigneeModel, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Creating Assignee Record for {}".format(assignee_request.name))
    assignee = method_create_assignee(shop_id, assignee_request)
    logging.info("Assignee Details: {}".format(assignee))
    return assignee

@app.get("/get-assignee")
async def get_assignee_by_id(assignee_id: str, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get Assignee: {}".format(assignee_id))
    assignee = method_get_assignee_by_id(shop_id=shop_id, assignee_id=assignee_id)
    logging.info("Assignee: {}".format(assignee))
    return assignee 

@app.get("/get-assignees")
async def get_assignees(request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    logging.info("Get Assignees for shop {}".format(shop_id))
    assignees = method_get_assignees(shop_id=shop_id)
    logging.info("Assignees: {}".format(assignees))
    return assignees 

@app.put("/update-assignee")
async def update_assignee(assignee_id: str, assignee_request: PutAssigneeModel, request: Request):
    shop_id = validate_user(token=request.headers.get('Authorization'))
    current_val = method_get_assignee_by_id(shop_id=shop_id, assignee_id=assignee_id)
    new_fields = assignee_request.model_dump(exclude_unset=True)

    current_services = current_val.pop('services')
    new_services = []

    if new_fields.get('services'):
        new_services = new_fields.pop('services')
        validate_services(shop_id=shop_id, service_ids=new_services)
    
    updated_assignee_data = reconstruct_updated_data(
        old_fields=current_val,
        model=PutAssigneeModel,
        new_fields=new_fields
    )
    
    updated_assignee_data.pop('services')
    updated_assignee = method_update_assignee(shop_id, assignee_id, updated_assignee_data)
    logging.info("Updated Assignee: {}".format(updated_assignee))

    if new_services:
        method_update_assigned_services(shop_id, current_services, new_services, updated_assignee)

    updated_assignee['services'] = method_get_services_by_assignee(assignee_id)

    return updated_assignee 

# @app.get("/test-endpoint")
# async def test_endpoint():
#     pass
    
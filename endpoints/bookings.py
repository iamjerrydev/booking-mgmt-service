from queries import *
from utils import *
from endpoints.service import validate_services
from endpoints.assignee import validate_assignees
from endpoints.task import method_get_tasks_by_booking, method_update_task, validate_slots
from datetime import datetime


def method_create_booking(input_item):

    new_services = [task['service_id'] for task in input_item.tasks]
    validate_services(shop_id=input_item.shop_id, service_ids=new_services)

    new_assignees = [task['assignee_id'] for task in input_item.tasks]
    validate_assignees(shop_id=input_item.shop_id, assignee_ids=new_assignees)

    # sort tasks by startdatetime
    tasks = sorted(input_item.tasks, key=lambda x:x['start_datetime'])

    if input_item.status not in ['Tentative', 'Confirmed', 'Completed']:
        logging.info("{} status is not allowed when creating a booking".format(input_item.status))
        raise HTTPException(status_code=400, 
                            detail="{} status is not allowed when creating a booking".format(input_item.status))
    
    booking_date = tasks[0]['start_datetime'][:10]

    task_slots = {}
    for task in tasks:

        if input_item.status == 'Tentative':
            task['status'] = 'To Do'
        elif input_item.status == 'Confirmed':
            task['status'] = 'Approved'
        else:
            task['status'] = 'Done'

        if not task['start_datetime'].startswith(booking_date) or not task['end_datetime'].startswith(booking_date):
            logging.info("Task dates must all be on the same date")
            raise HTTPException(status_code=400, detail="Task dates must all be on the same date")

        if not task_slots.get(task['assignee_id']):
            task_slots[task['assignee_id']] = []
        task_slots[task['assignee_id']].append({
            'start_time': task['start_datetime'][-5:],
            'end_time': task['end_datetime'][-5:]
        })

    for assignee in task_slots:
        if not validate_slots(shop_id=input_item.shop_id, 
                    booking_date=booking_date,
                    slots_for_checking=task_slots[assignee],
                    assignee_id=assignee):
            logging.info("Slot is no longer available.")
            raise HTTPException(status_code=400, detail="Slot is no longer available.")

    booking_record = {
        "booking_id": generate_id('booking'),
        "status": input_item.status,
        "shop_id": input_item.shop_id,
        "start_datetime": tasks[0]['start_datetime'],
        "customer": input_item.customer,
        "additional_fields": input_item.additional_fields,
        "remarks": input_item.remarks,
        "created_at": get_current_time(),
        "updated_at": get_current_time()
    }    
    booking_ref = booking_record['booking_id'][8:14].upper()
    booking_record.update({'booking_ref':booking_ref})
    db_create_booking(booking_record)
    
    for task in tasks:
        task_record = {
            "task_id": generate_id('task'),
            "booking_id": booking_record['booking_id'],
            "booking_ref": booking_ref,
            "status": task['status'],
            "shop_id": input_item.shop_id,
            "start_datetime": task['start_datetime'],
            "end_datetime": task['end_datetime'],
            "service_id": task['service_id'],
            "assignee_id": task['assignee_id']
        } 
        db_create_task(task_record)
        if not booking_record.get('tasks'):
            booking_record['tasks'] = []
        booking_record['tasks'].append(task_record)

    return booking_record

def method_get_booking_by_id(shop_id, booking_id, include_tasks=True):
    booking_record = db_get_booking_by_id(booking_id)
    if shop_id != booking_record['shop_id']:
        logging.info("Forbidden access to {}".format(booking_id))
        raise HTTPException(status_code=403, 
                            detail="Forbidden access to {}.".format(booking_id))
    if include_tasks: booking_record['tasks'] = method_get_tasks_by_booking(booking_id)
    return booking_record

def method_get_booking_by_ref(shop_id, booking_ref):
    booking_record = db_get_booking_by_ref(shop_id, booking_ref)
    if shop_id != booking_record['shop_id']:
        logging.info("Forbidden access to {}".format(booking_ref))
        raise HTTPException(status_code=403, 
                            detail="Forbidden access to {}.".format(booking_ref))
    booking_record['tasks'] = method_get_tasks_by_booking(booking_record['booking_id'])
    return booking_record

def method_get_bookings_by_date(shop_id, start_date, end_date):
    booking_records = db_get_bookings_by_date_range(shop_id, start_date, end_date)
    sorted_booking_records = sorted(booking_records, key=lambda x:x['startDateTime'])
    booking_list = [record['data'] for record in sorted_booking_records]
    return booking_list

def method_get_bookings_by_status(shop_id, start_date, end_date):
    booking_records = db_get_bookings_by_date_range(shop_id, start_date, end_date)
    sorted_booking_records = sorted(booking_records, key=lambda x:x['startDateTime'])
    booking_list = [record['data'] for record in sorted_booking_records]
    return group_bookings_by_status(booking_list)

def method_update_booking_status(shop_id, booking_id, status):
    booking = db_get_booking_by_id(booking_id)
    if booking['shop_id'] != shop_id:
        logging.info("Forbidden access to {}".format(booking_id))
        raise HTTPException(status_code=403, 
                            detail="Forbidden access to {}.".format(booking_id))

    updated_booking_record = db_update_booking_status(booking_id, status)['data']

    tasks, task_status = [], None
    if status == 'Tentative':
        task_records = db_get_tasks_by_booking_id(booking_id)
        tasks = [task['data']['task_id'] for task in task_records]
        task_status = 'To Do'
    elif status == 'Confirmed':
        task_records = db_get_tasks_by_booking_id(booking_id)
        tasks = [task['data']['task_id'] for task in task_records if task['status'] in ['To Do']]
        task_status = 'Approved'
    elif status == 'Completed':
        task_records = db_get_tasks_by_booking_id(booking_id)
        tasks = [task['data']['task_id'] for task in task_records if task['status'] in ['To Do', 'Approved', 'In Progress']]
        task_status = 'Done'
    if status in ['No Show', 'Declined']:
        task_records = db_get_tasks_by_booking_id(booking_id)
        tasks = [task['data']['task_id'] for task in task_records]
        task_status = 'Cancelled'

    for task_id in tasks:
        method_update_task(shop_id, booking_id, task_id, updated_data_fields={'status': task_status})

    updated_booking_record['tasks'] = method_get_tasks_by_booking(booking_id)
    return updated_booking_record

def method_update_booking(booking_id, updated_data_fields):
    updated_attrs = {}
    if updated_data_fields.get('customer'):
        if not ('name' in updated_data_fields['customer'] and 'mobile_no' in updated_data_fields['customer']):
            logging.info("Incomplete fields for customer details")
            raise HTTPException(status_code=400, 
                                detail="Incomplete fields for customer details")
    # if updated_data_fields.get('additional_fields'):
    #     validate_booking_fields()
    if updated_data_fields.get('updated_at'):
        updated_attrs['updatedAt'] =  updated_data_fields.get('updated_at')
    updated_booking_record = db_update_booking(booking_id, updated_data_fields, updated_attrs)['data'] 
    return updated_booking_record

def group_bookings_by_status(booking_list):
    data = {status: [] for status in ["For Approval", "Confirmed", "Past Due", "Completed", "No Show", "Declined"]}
    for booking in booking_list:
        tagging = ''
        if booking['status'] == 'Completed':
            tagging = 'Completed'
        elif booking['status'] == 'No Show':
            tagging = 'No Show'
        elif booking['status'] == 'Declined':
            tagging = 'Declined'
        elif datetime.strptime(booking['start_datetime'], '%Y-%m-%dT%H:%M') < datetime.now():
            tagging = 'Past Due'
        elif booking['status'] == 'Confirmed':
            tagging = 'Confirmed'
        else:
            tagging = 'For Approval'
        data[tagging].append(booking)
    return data

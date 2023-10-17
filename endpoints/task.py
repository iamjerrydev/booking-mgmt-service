from queries import *
from endpoints.service import validate_services
from endpoints.assignee import validate_assignees
from endpoints.shop import method_get_shop_by_id


def method_create_task(input_item):
    booking = db_get_booking_by_id(input_item.booking_id)

    if input_item.shop_id != booking['shop_id']:
        logging.info("Forbidden access to {}".format(input_item.booking_id))
        raise HTTPException(status_code=403, 
                            detail="Forbidden access to {}.".format(input_item.booking_id))
    
    if booking['status'] not in ['Tentative', 'Confirmed']:
        logging.info("Booking status must be either Tentative/Confirmed to add tasks.")
        raise HTTPException(status_code=400, 
                            detail="Task can only be added for Tentative and Confirmed Bookings")

    validate_services(shop_id=input_item.shop_id, service_ids=[input_item.service_id])
    validate_assignees(shop_id=input_item.shop_id, assignee_ids=[input_item.assignee_id])

    booking_date = booking['start_datetime'][:10]

    if not input_item.start_datetime.startswith(booking_date) or not input_item.end_datetime.startswith(booking_date):
        logging.info("Task dates must all be on the same date")
        raise HTTPException(status_code=400, detail="Task dates must all be on the same date")

    if not validate_slots(
        shop_id=input_item.shop_id,
        booking_date=booking_date,
        slots_for_checking=[{
            "start_time": input_item.start_datetime[-5:],
            "end_time": input_item.end_datetime[-5:]
        }],
        assignee_id=input_item.assignee_id
    ):
        logging.info("Slot is NOT already available.")
        raise HTTPException(status_code=400, detail="Slot is NOT already available.")

    task_record = {
        "task_id": generate_id('task'),
        "booking_id": input_item.booking_id,
        "booking_ref": input_item.booking_ref,
        "status": input_item.status,
        "shop_id": input_item.shop_id,
        "start_datetime": input_item.start_datetime,
        "end_datetime": input_item.end_datetime,
        "service_id": input_item.service_id,
        "assignee_id": input_item.assignee_id
    } 
    db_create_task(task_record)

    # update booking start date
    if task_record['start_datetime'] < booking['start_datetime']:
        updated_at_time = get_current_time()
        db_update_booking(input_item.booking_id, 
                            updated_data_fields={
                                'start_datetime': task_record['start_datetime'],
                                'updated_at': updated_at_time
                            }, 
                            updated_attrs={
                                'startDateTime': task_record['start_datetime'],
                                'updatedAt': updated_at_time
                            })

    return task_record

def method_get_tasks_by_booking(booking_id):
    task_records = db_get_tasks_by_booking_id(booking_id)
    sorted_task_records = sorted(task_records, key=lambda x:x['startDateTime'])
    task_list = [record['data'] for record in sorted_task_records]
    for idx, task in enumerate(task_list):
        task_list[idx]['date'] = task['start_datetime'][:10]
        task_list[idx]['start_time'] = task['start_datetime'][-5:]
        task_list[idx]['end_time'] = task['end_datetime'][-5:]
    return task_list

def method_get_tasks_by_date(shop_id, date_str, include_all):
    task_records = db_get_tasks_by_date(shop_id, date_str, include_all)
    sorted_task_records = sorted(task_records, key=lambda x:x['startDateTime'])
    task_list = [record['data'] for record in sorted_task_records]
    for idx, task in enumerate(task_list):
        task_list[idx]['date'] = task['start_datetime'][:10]
        task_list[idx]['start_time'] = task['start_datetime'][-5:]
        task_list[idx]['end_time'] = task['end_datetime'][-5:]
    return group_tasks_by_date(task_list)

def method_get_tasks_by_assignee(shop_id, assignee_id, start_date, end_date, include_all):
    validate_assignees(shop_id, assignee_ids=[assignee_id])
    task_records = db_get_tasks_by_assignee(assignee_id, start_date, end_date, include_all)
    sorted_task_records = sorted(task_records, key=lambda x:x['startDateTime'])
    task_list = [record['data'] for record in sorted_task_records]
    for idx, task in enumerate(task_list):
        task_list[idx]['date'] = task['start_datetime'][:10]
        task_list[idx]['start_time'] = task['start_datetime'][-5:]
        task_list[idx]['end_time'] = task['end_datetime'][-5:]
    return group_tasks_by_assignee(task_list, start_date, end_date)

def method_update_task(shop_id, booking_id, task_id, updated_data_fields):

    booking = db_get_booking_by_id(booking_id)
    booking['tasks'] = method_get_tasks_by_booking(booking_id)

    if shop_id != booking['shop_id'] or not any(task['task_id'] == task_id for task in booking['tasks']):
        logging.info("Forbidden access to {}".format(booking_id))
        raise HTTPException(status_code=403, 
                            detail="Forbidden access to {}.".format(booking_id))
    
    updated_attrs = {}

    if updated_data_fields.get('start_datetime'):
        
        updated_attrs['startDateTime'] =  updated_data_fields.get('start_datetime')
        booking_date = booking['start_datetime'][:10]

        if not updated_data_fields['start_datetime'].startswith(booking_date) or not updated_data_fields['end_datetime'].startswith(booking_date):
            logging.info("Task dates must all be on the same date")
            raise HTTPException(status_code=400, detail="Task dates must all be on the same date")

        print('updated_data_fields', updated_data_fields)
        if not validate_slots(
            shop_id=shop_id,
            booking_date=booking_date,
            slots_for_checking=[{
                "start_time": updated_data_fields.get('start_datetime')[-5:],
                "end_time": updated_data_fields.get('end_datetime')[-5:]
            }],
            assignee_id=updated_data_fields.get('assignee_id'),
            task_to_disregard=task_id
        ):
            logging.info("Slot is no longer available.")
            raise HTTPException(status_code=400, detail="Slot is NOT already available.")

    if updated_data_fields.get('assignee_id'):
        validate_assignees(shop_id=shop_id,assignee_ids=[updated_data_fields['assignee_id']])
        updated_attrs['assigneeId'] =  updated_data_fields['assignee_id']
    if updated_data_fields.get('status'):
        updated_attrs['status'] =  updated_data_fields.get('status')

    updated_at_time = get_current_time()
    updated_attrs['updatedAt'] =  updated_at_time
    updated_task_record = db_update_task(booking_id, task_id, updated_data_fields, updated_attrs)['data'] 

    if updated_data_fields.get('start_datetime'):
        if updated_data_fields['start_datetime'] < booking['start_datetime']:
            db_update_booking(booking_id, 
                              updated_data_fields={
                                  'start_datetime': updated_data_fields['start_datetime'],
                                  'updated_at': updated_at_time
                              }, 
                              updated_attrs={
                                  'startDateTime': updated_data_fields['start_datetime'],
                                  'updatedAt': updated_at_time
                              })

    return updated_task_record

def method_delete_task(shop_id, booking_id, task_id):

    booking = db_get_booking_by_id(booking_id)
    tasks = method_get_tasks_by_booking(booking_id)

    if len(tasks) <= 1:
        logging.info("To delete a task, the booking must have at least one task")
        raise HTTPException(status_code=400, 
                            detail="To delete a task, the booking must have at least one task")

    sorted_tasks = sorted(tasks, key=lambda x:x['start_datetime'])
    task = next(iter(task for task in sorted_tasks if task['task_id'] == task_id), None)

    if shop_id != booking['shop_id'] or not task:
        logging.info("Forbidden access to {}".format(task_id))
        raise HTTPException(status_code=403, 
                            detail="Forbidden access to {}.".format(task_id))
    
    db_delete_task_by_id(booking_id, task_id)

    # update start date
    if sorted_tasks[0]['task_id'] == task_id:
        updated_at_time = get_current_time()
        db_update_booking(booking_id, 
                            updated_data_fields={
                                'start_datetime': sorted_tasks[1]['start_datetime'],
                                'updated_at': updated_at_time
                            }, 
                            updated_attrs={
                                'startDateTime': sorted_tasks[1]['start_datetime'],
                                'updatedAt': updated_at_time
                            })

def group_tasks_by_date(task_list):
    data = {}
    for task in task_list:
        date = task['start_datetime'][:10]
        if not data.get(date):
            data.update({date:{}})
        assignee = task['assignee_id']
        if not data[date].get(assignee):
            data[date].update({assignee:[]})
        data[date][assignee].append(task)
    return data

def group_tasks_by_assignee(task_list, start_date=None, end_date=None):
    data = {}
    for task in task_list:
        date = task['start_datetime'][:10]
        assignee = task['assignee_id']
        if not data.get(assignee):
            data.update({assignee:{}})
            _start_date = datetime.strptime(start_date, '%Y-%m-%d')
            _end_date = datetime.strptime(end_date, '%Y-%m-%d')
            for diff in range(int((_end_date - _start_date).days) + 1):
                data[assignee][datetime.strftime(_start_date + timedelta(days=diff), "%Y-%m-%d")] = []
        data[assignee][date].append(task)
    return data

def validate_slots(shop_id, booking_date, slots_for_checking, assignee_id, excluded_slots=None, task_to_disregard=None):
    available_hrs = get_available_time_windows(shop_id, booking_date, assignee_id, task_to_disregard=task_to_disregard)
    is_available = [None] * len(slots_for_checking)
    for idx, slot in enumerate(slots_for_checking):
        x1_start = datetime.strptime(slot['start_time'], '%H:%M').time()
        x1_end = datetime.strptime(slot['end_time'], '%H:%M').time()
        for ahour in available_hrs:
            a1_start = datetime.strptime(ahour['start_time'], '%H:%M').time()
            a1_end = datetime.strptime(ahour['end_time'], '%H:%M').time()
            if a1_start <= x1_start < a1_end and x1_end <= a1_end: 
                is_available[idx] = True
                break
        if not is_available[idx]: is_available[idx] = False
    return all(is_available)

def get_available_time_windows(shop_id, booking_date, assignee_id, excluded_slots=None, task_to_disregard=None):
    day = datetime.strptime(booking_date, '%Y-%m-%d').strftime('%A')
    available_hrs = method_get_shop_by_id(shop_id)['operating_hours'][day]
    existing_tasks = method_get_tasks_by_assignee(
        shop_id, assignee_id, 
        booking_date, booking_date, 
        include_all=False)[assignee_id].get(booking_date)
    existing_bookings = [
        {
            'start_time': task['start_datetime'][-5:],
            'end_time': task['end_datetime'][-5:]
        } for task in existing_tasks if task['task_id'] != task_to_disregard
    ] if existing_tasks else []
    if excluded_slots: existing_bookings.append(excluded_slots)
    if existing_bookings: existing_bookings = sorted(existing_bookings, key=lambda x:x['start_time'])
    for exclusion in existing_bookings:
        x1_start = datetime.strptime(exclusion['start_time'], '%H:%M').time()
        x1_end = datetime.strptime(exclusion['end_time'], '%H:%M').time()
        for idx, ahour in enumerate(available_hrs):
            a1_start = datetime.strptime(ahour['start_time'], '%H:%M').time()
            a1_end = datetime.strptime(ahour['end_time'], '%H:%M').time()
            if a1_start < x1_start < a1_end and x1_end < a1_end:
                available_hrs[idx]['end_time'] = x1_start.strftime("%H:%M")
                available_hrs.insert(idx + 1, {
                    'start_time': x1_end.strftime("%H:%M"),
                    'end_time': a1_end.strftime("%H:%M")
                })
                break
            if a1_start < x1_start < a1_end and x1_end == a1_end:
                available_hrs[idx]['end_time'] = x1_start.strftime("%H:%M")
                break
            if a1_start == x1_start and a1_start < x1_end < a1_end:
                available_hrs[idx]['start_time'] = x1_end.strftime("%H:%M")
                break
            if a1_start == x1_start and x1_end == a1_end:
                available_hrs.remove(ahour)
                break
            if idx + 1 < len(available_hrs):
                a2_start = datetime.strptime(available_hrs[idx+1]['start_time'], '%H:%M').time()
                if a1_start < x1_start < a1_end and a1_end < x1_end <= a2_start:
                    available_hrs[idx]['end_time'] = x1_start.strftime("%H:%M")
                    break
                if a1_start < x1_start < a1_end and (x1_end > a1_end and x1_end > a2_start):
                    available_hrs[idx]['end_time'] = x1_start.strftime("%H:%M")
                    available_hrs[idx+1]['start_time'] = x1_end.strftime("%H:%M")
                    break
    return available_hrs

def method_get_available_slots(shop_id, booking_date, duration, assignee_id=None, excluded_slots=None):

    # get assignees

    # per assignee
    available_windows = get_available_time_windows(shop_id, booking_date, assignee_id, excluded_slots)
    print("available_windows", available_windows)

    available_slots = []

    for window in available_windows:
        window_start = datetime.strptime(window['start_time'], '%H:%M')
        window_end = datetime.strptime(window['end_time'], '%H:%M')
        time_diff_in_mins = int((window_end - window_start).seconds / 60)
        if time_diff_in_mins == duration:
            available_slots.append(window)
            continue
        elif time_diff_in_mins > duration:
            for ctr in range(int(time_diff_in_mins / 30)):
                start_time = window_start + timedelta(minutes=(30*ctr))
                end_time = start_time + timedelta(minutes=duration)
                if end_time > window_end: continue
                available_slots.append({
                    'start_time': start_time.strftime("%H:%M"),
                    'end_time': end_time.strftime("%H:%M"),
                })
        else:
            continue

    return available_slots

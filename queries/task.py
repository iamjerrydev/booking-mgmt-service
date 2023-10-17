import logging
from fastapi import HTTPException
from utils import *
from boto3.dynamodb.conditions import Key, Attr

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def db_create_task(task_record):
    item = {
        "PK": task_record.get('booking_id'),
        "SK": "T:{}".format(task_record.get('task_id')),
        "type": "task",
        "shopId": task_record.get('shop_id') + "_tasks",
        "assigneeId": task_record.get('assignee_id'),
        "status": task_record.get('status'),
        "startDateTime": task_record.get('start_datetime'),
        "data": task_record,
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
    }
    return create_item(item=item)

def db_get_task_by_id(booking_id, task_id):
    task_record = get_item(key={"PK": booking_id, "SK":"T:{}".format(task_id)})
    if not task_record:
        logging.info("Task {} not found.".format(task_id))
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    return task_record['data']

def db_get_tasks_by_booking_id(booking_id):
    booking_tasks = query_items_by_condition(
        condition_exp=Key('PK').eq(booking_id) & Key('SK').begins_with('T:')
    )
    return booking_tasks['Items']

def db_get_tasks_by_date(shop_id, dates_str, include_all):
    filter = None if include_all else Attr('status').ne('Cancelled')
    booking_records = query_indexed_items_by_condition(
        condition_exp=Key('shopId').eq(shop_id + '_tasks') & Key('startDateTime').begins_with(dates_str),
        index_name='GS2',
        filter=filter
    )
    return booking_records['Items']

def db_get_tasks_by_assignee(assignee_id, start_date, end_date, include_all):
    filter = None if include_all else Attr('status').ne('Cancelled')
    booking_records = query_indexed_items_by_condition(
        condition_exp=Key('assigneeId').eq(assignee_id) & Key('startDateTime').between(start_date + 'T00:00', end_date + 'T23:59'),
        index_name='GS3',
        filter=filter
    )
    return booking_records['Items']

def db_update_task(booking_id, task_id, updated_data_fields, updated_attrs):
    update_attr_dict = get_update_data_attrs(updated_data_fields)
    new_update_attr_dict = add_update_attrs(update_attr_dict=update_attr_dict, fields_for_update=updated_attrs)
    print('UPDATE QUERY:' + str(new_update_attr_dict))
    assignee_record = update_item(
        key={"PK": booking_id, "SK":"T:{}".format(task_id)},
        update_expression=new_update_attr_dict['update_expression'],
        exp_attr_values=new_update_attr_dict['exp_attr_values'],
        exp_attr_names=new_update_attr_dict['exp_attr_names']
    )
    return assignee_record['Attributes']

def db_delete_task_by_id(booking_id, task_id):
    delete_item(key={"PK": booking_id, "SK":"T:{}".format(task_id)})
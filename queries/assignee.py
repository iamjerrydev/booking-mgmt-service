import logging
from fastapi import HTTPException
from utils import *
from boto3.dynamodb.conditions import Key, Attr

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def db_create_assignee(assignee_record):
    item = {
        "PK": assignee_record.get('shop_id'),
        "SK": "A:{}".format(assignee_record.get('assignee_id')),
        "type": "assignee",
        "data": assignee_record,
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
    }
    create_item(item=item)

def db_get_assignee_by_id(shop_id, assignee_id):
    assignee_record = get_item(key={"PK": shop_id, "SK":"A:{}".format(assignee_id)})

    if not assignee_record:
        logging.info("Assignee {} not found.".format(assignee_id))
        raise HTTPException(status_code=404, detail=f"Assignee {assignee_id} not found.")

    return assignee_record

def db_get_assignees(shop_id):
    assignee_record = query_items_by_condition(
        condition_exp=Key('PK').eq(shop_id) & Key('SK').begins_with('A:')
    )
    return assignee_record['Items']

def db_get_assignees_by_service(service_id):
    service_assignees = query_items_by_condition(
        condition_exp=Key('PK').eq(service_id) & Key('SK').begins_with('A:')
    )
    return service_assignees['Items']

def db_update_assignee(shop_id, assignee_id, updated_fields):
    update_attr_dict = get_update_data_attrs(updated_fields)
    assignee_record = update_item(
        key={"PK": shop_id, "SK":"A:{}".format(assignee_id)},
        update_expression=update_attr_dict['update_expression'],
        exp_attr_values=update_attr_dict['exp_attr_values'],
        exp_attr_names=update_attr_dict['exp_attr_names']
    )
    return assignee_record['Attributes']

def db_add_assigned_service(assignee_id, service_data):
    item = {
            "PK": assignee_id,
            "SK": "S:{}".format(service_data.get('service_id')),
            "type": "assignedService",
            "data": service_data,
            "createdAt": get_current_time(),
            "updatedAt": get_current_time()
        }
    create_item(item=item)

def db_update_service_assignee(service_id, assignee_id, assignee_data):
    update_item(
        key={"PK": service_id, "SK":"A:{}".format(assignee_id)},
        update_expression="set #data = :data",
        exp_attr_values={':data': assignee_data},
        exp_attr_names={'#data': 'data'}
    )

def db_delete_service_assignee_records(service_id, assignee_id):
    delete_item(key={"PK": assignee_id, "SK":"S:{}".format(service_id)})
    delete_item(key={"PK": service_id, "SK":"A:{}".format(assignee_id)})

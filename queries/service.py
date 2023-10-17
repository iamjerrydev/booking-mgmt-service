import logging
from fastapi import HTTPException
from utils import *
from boto3.dynamodb.conditions import Key, Attr

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def db_create_service(shop_id, service_record):
    item = {
        "PK": shop_id,
        "SK": "S:{}".format(service_record.get('service_id')),
        "type": "service",
        "data": service_record,
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
    }
    create_item(item=item)

def db_get_service_by_id(shop_id, service_id):
    service_record = get_item(key={"PK": shop_id, "SK":"S:{}".format(service_id)})
    if not service_record:
        logging.info("Service {} not found.".format(service_id))
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found.")
    return  service_record

def db_get_services_by_assignee(assignee_id):
    assigned_services = query_items_by_condition(
        condition_exp=Key('PK').eq(assignee_id) & Key('SK').begins_with('S:')
    )
    return assigned_services['Items']

def db_get_services(shop_id):
    service_record = query_items_by_condition(
        condition_exp=Key('PK').eq(shop_id) & Key('SK').begins_with('S:')
    )
    return service_record['Items']

def db_update_service(shop_id, service_id, updated_fields):
    update_attr_dict = get_update_data_attrs(updated_fields)
    service_record = update_item(
        key={"PK": shop_id, "SK":"S:{}".format(service_id)},
        update_expression=update_attr_dict['update_expression'],
        exp_attr_values=update_attr_dict['exp_attr_values'],
        exp_attr_names=update_attr_dict['exp_attr_names']
    )
    return service_record['Attributes']

def db_add_service_assignee(service_id, assignee_data):
    item = {
            "PK": service_id,
            "SK": "A:{}".format(assignee_data.get('assignee_id')),
            "type": "serviceAssignee",
            "data": assignee_data,
            "createdAt": get_current_time(),
            "updatedAt": get_current_time()
        }
    create_item(item=item)

def db_update_assigned_service(assignee_id, service_id, service_data):
    update_item(
        key={"PK": assignee_id, "SK":"S:{}".format(service_id)},
        update_expression="set #data = :data",
        exp_attr_values={':data': service_data},
        exp_attr_names={'#data': 'data'}
    )

def db_delete_assigned_service_records(assignee_id, service_id):
    delete_item(key={"PK": assignee_id, "SK":"S:{}".format(service_id)})
    delete_item(key={"PK": service_id, "SK":"A:{}".format(assignee_id)})

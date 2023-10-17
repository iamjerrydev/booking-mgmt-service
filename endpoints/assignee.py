from queries import *
from utils import *

def method_create_assignee(shop_id, input_item):

    db_get_shop_by_id(shop_id)
    shop_services = [service['data']['service_id'] for service in db_get_services(shop_id)]
    if not all(item in shop_services for item in input_item.services):
        logging.info("Some services are not found.") 
        missing_ids = set(input_item.services).difference(set(shop_services))
        raise HTTPException(status_code=400, 
                            detail="Some services not found: {}".format(str(missing_ids)))

    assignee_record = {
        "assignee_id": generate_id('assignee'),
        "name": input_item.name,
        "shop_id": shop_id,
        "role": input_item.role,
        "photo_url": input_item.photo_url,
        "accept_booking": input_item.accept_booking,
        "availability": input_item.availability,
        "leaves": input_item.leaves
    }
    db_create_assignee(assignee_record)

    for service in input_item.services:
        db_add_assigned_service(
            assignee_id=assignee_record.get('assignee_id'), 
            service_data=db_get_service_by_id(shop_id, service)['data']
            )
        db_add_service_assignee(service_id=service, assignee_data=assignee_record)

    assignee_record.update({'services':input_item.services})
    return assignee_record

def method_get_assignee_by_id(shop_id, assignee_id):
    assignee_record = db_get_assignee_by_id(shop_id, assignee_id)['data']
    if assignee_record['shop_id'] != shop_id:
        logging.info("Forbidden Access.")
        raise HTTPException(status_code=403, detail=f"Forbidden Access.")
    services = db_get_services_by_assignee(assignee_id)
    assignee_record['services'] = [service['data']['service_id'] for service in services]
    return assignee_record

def method_get_assignees(shop_id):
    assignee_records = db_get_assignees(shop_id)
    return [assignee['data'] for assignee in assignee_records]

def method_update_assignee(shop_id, assignee_id, updated_fields):
    updated_assignee_record = db_update_assignee(shop_id, assignee_id, updated_fields)['data'] 
    return updated_assignee_record

def method_update_assigned_services(shop_id, current_services, new_services, assignee_data):

    for_update = set(new_services).intersection(set(current_services))
    print('for update' + str(for_update))
    for service in for_update:
        db_update_service_assignee(service, assignee_data['assignee_id'], assignee_data)

    for_deletion = set(current_services).difference(set(new_services))
    print('for deletion' + str(for_deletion))
    for service in for_deletion:
        db_delete_service_assignee_records(service, assignee_data['assignee_id'])

    for_creation = set(new_services).difference(set(current_services))
    print('for creation' + str(for_creation))
    for service in for_creation:
        db_add_assigned_service(
            assignee_id=assignee_data['assignee_id'], 
            service_data=db_get_service_by_id(shop_id, service)['data']
            )
        db_add_service_assignee(service_id=service, assignee_data=assignee_data)

def method_get_assignees_by_service(service_id):
    assignees = db_get_assignees_by_service(service_id)
    service_assignees = [assignee['data']['assignee_id'] for assignee in assignees]
    return service_assignees

def validate_assignees(shop_id, assignee_ids):
    shop_assignees = [assignee['assignee_id'] for assignee in method_get_assignees(shop_id=shop_id)]
    if not all(item in shop_assignees for item in assignee_ids):
        logging.info("Some assignees are not found.")
        missing_ids = set(assignee_ids).difference(set(shop_assignees))
        raise HTTPException(status_code=400, 
                            detail="Some assignees not found: {}".format(str(missing_ids)))
from queries import *
from utils import *
from endpoints.assignee import method_get_assignees_by_service, validate_assignees

def method_create_service(shop_id, input_item):

    db_get_shop_by_id(shop_id)
    validate_assignees(shop_id, input_item.assignees)

    service_record = {
        "service_id": generate_id('service'),
        "title": input_item.title,
        "shop_id": shop_id,
        "description": input_item.description,
        "photo_url": input_item.photo_url,
        "duration": input_item.duration,
        "amount": input_item.amount,
        "is_active": input_item.is_active,
        "remarks": input_item.remarks
    }    
    db_create_service(shop_id, service_record)

    for assignee in input_item.assignees:
        db_add_service_assignee(
            service_id=service_record.get('service_id'), 
            assignee_data=db_get_assignee_by_id(shop_id, assignee)['data']
            )
        db_add_assigned_service(assignee_id=assignee, service_data=service_record)

    service_record.update({'assignees':input_item.assignees})
        
    return service_record

def method_get_service_by_id(shop_id, service_id):

    service_record = db_get_service_by_id(shop_id, service_id)['data']

    if service_record['shop_id'] != shop_id:
        logging.info("Forbidden Access.")
        raise HTTPException(status_code=403, detail=f"Forbidden Access.")
    
    service_record['assignees'] = method_get_assignees_by_service(service_id)

    return service_record

def method_get_services(shop_id):
    service_records = db_get_services(shop_id)
    return [service['data'] for service in service_records]

def method_update_service(shop_id, service_id, updated_fields):
    updated_service_record = db_update_service(shop_id, service_id, updated_fields)['data'] 
    return updated_service_record

def method_update_service_assignees(shop_id, current_assignees, new_assignees, service_data):

    for_update = set(new_assignees).intersection(set(current_assignees))
    print('for update' + str(for_update))
    for assignee in for_update:
        db_update_assigned_service(assignee, service_data['service_id'], service_data)

    for_deletion = set(current_assignees).difference(set(new_assignees))
    print('for deletion' + str(for_deletion))
    for assignee in for_deletion:
        db_delete_assigned_service_records(assignee, service_data['service_id'])

    for_creation = set(new_assignees).difference(set(current_assignees))
    print('for creation' + str(for_creation))
    for assignee in for_creation:
        db_add_service_assignee(
            service_id=service_data['service_id'], 
            assignee_data=db_get_assignee_by_id(shop_id, assignee)['data']
        )
        db_add_assigned_service(assignee_id=assignee, service_data=service_data)
        
def method_get_services_by_assignee(assignee_id):
    services = db_get_services_by_assignee(assignee_id)
    assignee_services = [service['data']['service_id'] for service in services]
    return assignee_services

def validate_services(shop_id, service_ids):
    shop_services = [service['service_id'] for service in method_get_services(shop_id=shop_id)]
    if not all(item in shop_services for item in service_ids):
        logging.info("Some services are not found.")
        missing_ids = set(service_ids).difference(set(shop_services))
        raise HTTPException(status_code=400, 
                            detail="Some services not found: {}".format(str(missing_ids)))
                            
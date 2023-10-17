import logging
from fastapi import HTTPException
from utils import *
from boto3.dynamodb.conditions import Key, Attr

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def db_create_booking(booking_record):
    item = {
        "PK": booking_record.get('booking_id'),
        "SK": "A",
        "type": "booking",
        "shopId": booking_record.get('shop_id'),
        "status": booking_record.get('status'),
        "startDateTime": booking_record.get('start_datetime'),
        "bookingRef": booking_record.get('booking_ref'),
        "data": booking_record,
        "createdAt": booking_record.get('created_at'),
        "updatedAt": booking_record.get('updated_at')
    }
    create_item(item=item)


def db_get_booking_by_id(booking_id):
    booking_record = get_item(key={"PK": booking_id, "SK":"A"})
    if not booking_record:
        logging.info("Booking {} not found.".format(booking_id))
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found.")
    return booking_record['data']

def db_get_booking_by_ref(shop_id, booking_ref):
    booking_record = query_indexed_items_by_condition(
        condition_exp=Key('shopId').eq(shop_id) & Key('bookingRef').eq(booking_ref),
        index_name='GS4'
    )
    if not booking_record['Items']:
        logging.info("Booking {} not found.".format(booking_ref))
        raise HTTPException(status_code=404, detail=f"Booking {booking_ref} not found.")
    return booking_record['Items'][0]['data']

def db_get_bookings_by_date_range(shop_id, start_date, end_date):
    booking_records = query_indexed_items_by_condition(
        condition_exp=Key('shopId').eq(shop_id) & Key('startDateTime').between(start_date + 'T00:00', end_date + 'T23:59'),
        index_name='GS2'
    )
    return booking_records['Items']

def db_update_booking_status(booking_id, status):
    updated_at = get_current_time()
    assignee_record = update_item(
        key={"PK": booking_id, "SK":"A"},
        update_expression="set #data.#status= :status_val, #data.#updated_at= :updatedAt_val, #status= :status_val, #updatedAt= :updatedAt_val",
        exp_attr_values={':status_val': status, ':updatedAt_val': updated_at},
        exp_attr_names={'#data': 'data', '#status': 'status', '#updated_at': 'updated_at', '#updatedAt': 'updatedAt'}
    )
    return assignee_record['Attributes']

def db_update_booking(booking_id, updated_data_fields, updated_attrs):
    update_attr_dict = get_update_data_attrs(updated_data_fields)
    new_update_attr_dict = add_update_attrs(update_attr_dict=update_attr_dict, fields_for_update=updated_attrs)
    assignee_record = update_item(
        key={"PK": booking_id, "SK":"A"},
        update_expression=new_update_attr_dict['update_expression'],
        exp_attr_values=new_update_attr_dict['exp_attr_values'],
        exp_attr_names=new_update_attr_dict['exp_attr_names']
    )
    return assignee_record['Attributes']
import logging
from fastapi import HTTPException
from utils import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def db_create_shop(shop_record):
    item = {
        "PK": shop_record.get('shop_id'),
        "SK": "A",
        "type": "shop",
        "slug": shop_record.get('slug'),
        "data": shop_record,
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
    }
    create_item(item=item)

def db_get_shop_by_id(shop_id):
    shop_record = get_item(key={"PK": shop_id, "SK":"A"})
    if not shop_record:
        raise HTTPException(status_code=404, detail=f"Shop {shop_id} not found.")
        logging.info("Shop {} not found.".format(shop_id))
    return shop_record

def db_update_shop(shop_id, fields_for_update):
    update_attr_dict = get_update_data_attrs(fields_for_update)
    shop_record = update_item(
        key={"PK": shop_id, "SK":"A"},
        update_expression=update_attr_dict['update_expression'],
        exp_attr_values=update_attr_dict['exp_attr_values'],
        exp_attr_names=update_attr_dict['exp_attr_names']
    )
    return shop_record['Attributes']

# SHOP SETTINGS

def db_add_shop_setting(shop_id, shop_setting):
    item = {
        "PK": shop_id,
        "SK": "Setting",
        "type": "shopSetting",
        "data": shop_setting,
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
    }
    create_item(item=item)

def db_get_shop_settings(shop_id):
    shop_setting_record = get_item(key={"PK": shop_id, "SK":"Setting"})
    if not shop_setting_record:
        logging.info("Shop setting for {} not found.".format(shop_id))
        raise HTTPException(status_code=404, detail=f"Shop setting for {shop_id} not found.")
    return shop_setting_record

def db_update_shop_settings(shop_id, updated_fields):
    update_attr_dict = get_update_data_attrs(updated_fields)
    shop_setting_record = update_item(
        key={"PK": shop_id, "SK":"Setting"},
        update_expression=update_attr_dict['update_expression'],
        exp_attr_values=update_attr_dict['exp_attr_values'],
        exp_attr_names=update_attr_dict['exp_attr_names']
    )
    return shop_setting_record['Attributes']
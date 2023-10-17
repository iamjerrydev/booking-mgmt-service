from queries import *
from utils import *
from models.shop import ShopSettingModel


def method_create_shop(input_item):

    shop_record = {
        "shop_id": input_item.shop_id,
        "name": input_item.name,
        "is_active": input_item.is_active,
        "slug": input_item.slug,
        "logo": input_item.logo,
        "email": input_item.email,
        "description": input_item.description,
        "operating_hours": input_item.operating_hours
    }    
    db_create_shop(shop_record)

    shop_default_setting = ShopSettingModel()
    db_add_shop_setting(shop_record['shop_id'], shop_default_setting.model_dump())

    return shop_record

def method_get_shop_by_id(shop_id):
    shop_record = db_get_shop_by_id(shop_id)['data']
    return shop_record

def method_update_shop(shop_id, updated_fields):
    updated_shop_record = db_update_shop(shop_id, updated_fields)
    return updated_shop_record['data'] 

def method_get_shop_setting_by_id(shop_id):
    shop_setting_record = db_get_shop_settings(shop_id)['data']
    # also get questionnaires and notifications
    return shop_setting_record

def method_update_shop_settings(shop_id, updated_fields):
    updated_shop_setting_record = db_update_shop_settings(shop_id, updated_fields)
    return updated_shop_setting_record['data'] 

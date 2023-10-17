import boto3
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


client = boto3.resource("dynamodb")
# table_name = os.environ["TABLE_NAME"]
table_name = "data_dev"
# table = dynamodb.Table(table_name)

def get_item(key):
    table = client.Table(table_name)
    item = table.get_item(Key=key).get("Item")
    logging.info("Retrived Item: {}".format(str(item)))
    return item

def create_item(item):
    table = client.Table(table_name)
    logging.info("Inserting Item: {}".format(str(item)))
    item = table.put_item(Item=item, ReturnValues='ALL_OLD')
    return item

def query_items_by_condition(condition_exp):
    table = client.Table(table_name)
    items = table.query(
        KeyConditionExpression=condition_exp
    )
    logging.info("Queried Items: {}".format(str(items)))
    return items

def query_indexed_items_by_condition(condition_exp, index_name, filter=None):
    table = client.Table(table_name)
    items = table.query(
        IndexName=index_name,
        KeyConditionExpression=condition_exp,
        FilterExpression=filter
    ) if filter else table.query(
        IndexName=index_name,
        KeyConditionExpression=condition_exp
    )
    logging.info("Queried Items: {}".format(str(items)))
    return items

def update_item(key, update_expression, exp_attr_values, exp_attr_names):
    table = client.Table(table_name)
    item = table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=exp_attr_values,
        ExpressionAttributeNames=exp_attr_names,
        ReturnValues='ALL_NEW'
    )
    logging.info("Updated Item: {}".format(str(item)))
    return item

def delete_item(key):
    table = client.Table(table_name)
    item = table.delete_item(Key=key)
    logging.info("Deleted Item: {}".format(str(item)))

def get_update_data_attrs(fields_for_update):
    
    update_attr_dict = {
        'update_expression': "set ",
        'exp_attr_values': {},
        'exp_attr_names': {'#data': 'data'}
    }

    for field in fields_for_update:
        update_attr_dict['update_expression'] = update_attr_dict['update_expression'] + '#data.#{0}= :{0}_val, '.format(field)
        update_attr_dict['exp_attr_values'].update({':{}_val'.format(field): fields_for_update[field]})
        update_attr_dict['exp_attr_names'].update({'#{}'.format(field): field})

    update_attr_dict['update_expression'] = update_attr_dict['update_expression'][:-2]

    return update_attr_dict

def add_update_attrs(update_attr_dict, fields_for_update):

    update_attr_dict['update_expression'] = update_attr_dict['update_expression'] + ', '

    for field in fields_for_update:
        update_attr_dict['update_expression'] = update_attr_dict['update_expression'] + '#{0}= :{0}_val, '.format(field)
        update_attr_dict['exp_attr_values'].update({':{}_val'.format(field): fields_for_update[field]})
        update_attr_dict['exp_attr_names'].update({'#{}'.format(field): field})

    update_attr_dict['update_expression'] = update_attr_dict['update_expression'][:-2]

    return update_attr_dict
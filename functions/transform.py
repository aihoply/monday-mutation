import json
import re

def transform_columns_to_graphql_format(columns_json):

    columns_json = json.loads(columns_json)
    graphQL_values = {}
    value_update = None
    value_update_found = False
    
    for column in columns_json['data']['columns']:

        if column['type'] == 'email':
            email_value = {"text": column['value'], "email": column['value']}
            graphQL_values[column['id']] = email_value

        elif column['type'] == 'board_relation':
            item_ids = column.get('value', [])
            if not isinstance(item_ids, list):
                item_ids = [item_ids]
            board_relation_value = {"item_ids": item_ids}
            graphQL_values[column['id']] = board_relation_value

        elif column['type'] == 'link':
            link_value = {"url": column['value'], "text": column['value']}
            graphQL_values[column['id']] = link_value

        elif column['type'] == 'date':
            date_value = {"date": column['value']}
            graphQL_values[column['id']] = date_value
            
        else:
            graphQL_values[column['id']] = column['value']
    
    if 'updates' in columns_json['data']:
        value_update = columns_json['data']['update']
        value_update_found = True

    graphQL_values_str = json.dumps(graphQL_values)
    
    return graphQL_values_str, value_update, value_update_found

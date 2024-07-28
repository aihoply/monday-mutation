from flask import Flask, request, jsonify
import json
import time
from openai import OpenAI
from pymongo import MongoClient
import configparser
import multiprocessing
import json
import time
from test_mutaition import QueryMondayApi, MutationMondayApi
from bots.fill_data_bot import fill_data_to_columns
import requests
import os
import time
from functions import create, modify, delete, add_update
app = Flask(__name__)

BOARD_IDS =

import json

def transform_columns_to_graphql_format(columns_json):
    # Transform into the required dictionary format
    column_values = {}
    value_update = None
    value_update_found = False
    
    for column in columns_json['columns']:
        if column['type'] == 'email':
            # Ensure the email column is in the correct format
            email_value = {
                "text": column['value'],
                "email": column['value']
            }
            column_values[column['id']] = email_value
        elif column['type'] == 'board_relation':
            item_ids = column.get('value', [])
            if not isinstance(item_ids, list):
                item_ids = [item_ids]
            board_relation_value = {
                "item_ids": item_ids
            }
            column_values[column['id']] = board_relation_value
        elif column['type'] == 'link':
            # If link column is found, store the value in the required format
            link_value = {
                "url": column['value'],
                "text": "Go to link"  # Example hardcoded text, replace with column['text'] if available
            }
            column_values[column['id']] = link_value
        elif column['type'] == 'date':
            # If date column is found, store the value in the required format
            date_value = {
                "date": column['value']
            }
            column_values[column['id']] = date_value
        else:
            column_values[column['id']] = column['value']
    
    # Handle updates separately
    if 'updates' in columns_json and columns_json['updates']:
        update_dict = columns_json['updates'][0]
        if 'body' in update_dict:
            value_update = update_dict['body']
            value_update_found = True

    # Convert to JSON string and escape double quotes
    column_values_str = json.dumps(column_values).replace('"', '\\"')
    
    return column_values_str, value_update, value_update_found

def query_item_id(collection, query):
  return "1886595969"

@app.route('/create-item', methods=['POST'])
def create_item1():
    data = request.get_json()
    mutation_type = data.get('mutation_type')
    board_related = data.get('board_related')
    group_related  = data.get('group_related')
    values = data.get('values')
    item_name = data.get('item_name')

    if mutation_type == "create":
        start_time = time.time()
        print("Bắt đầu tạo item")
        board_id = BOARD_IDS.get(board_related)
        print('wait get board column')
        columns_format = QueryMondayApi.get_board_columns(board_id=board_id)
        end_time = time.time()  # End the timer
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
        fill_data = fill_data_to_columns(columns_format=columns_format, data_input=values)
        print('done filling data')
        colums, value_update, value_update_found = transform_columns_to_graphql_format(fill_data)
        t2 = create.(board_id, item_name, colums)
        if isinstance(t2, str):
            t2 = json.loads(t2)
        print(t2)

        item_id = t2["data"]["create_item"]["id"]
        print("ID vừa tạo :", item_id)
        
        print(value_update_found)
        t1 = None  # Initialize t1 to ensure it's defined
        if value_update_found:
            print(value_update)
            t1 = create_update(item_id, value_update)
            print(t1)

        return jsonify({"item_id": item_id, "update_response": t1})
    else:
        return jsonify({"error": "Invalid mutation_type"}), 400
    
@app.route('/modify-item', methods=['POST'])
def modify_item():
    data = request.get_json()
    board_related = data.get('board_related')
    group_related  = data.get('group_related')
    values = data.get('values')

    print("Bắt đầu Chỉnh sửa item")
    board_id = BOARD_IDS.get(board_related)
    print('wait get board column')
    columns_format = QueryMondayApi.get_board_columns(board_id=board_id)
    print("done get board column")
    print('----')
    print('wait filling data')

    if isinstance(values, list):
        values = ''.join(values)

    fill_data = fill_data_to_columns(columns_format=columns_format, data_input=values)
    print('done filling data')
    print(fill_data)
    
    if isinstance(fill_data, str):
        fill_data = json.loads(fill_data)
    colums, value_update, value_update_found = transform_columns_to_graphql_format(fill_data)
    print(colums)
    print("Start motify")
    print(board_id)
    print("---")
    print("Tìm ID")
    item_id1 = query_items(datatotal)
    temp = send_graphql_request(item_id1, board_id, colums)
    print(temp)
    if value_update_found == True:
        print(value_update)
        t1 = create_update(item_id1, value_update)
        print(t1)
        return jsonify({"item_id": item_id1, "update_response": t1})
    else:
        return jsonify({"item_id": item_id1, "status": temp})
    

@app.route('/delete-item', methods=['POST'])
def delete_item_route():
    data = request.get_json()
    board_related = data.get('board_related')
    values = data.get('values')
    confirm_delete = data.get('confirm_delete')

    print("Starting delete process")
    
    if isinstance(values, list):
        values = ''.join(values)

    with open("./prompt_temp.txt", 'r', encoding='utf-8') as fo:
        temp = fo.readlines()

    temp = ''.join(temp)

    datatotal = "prompt and check intent user and necessary data :" + temp + values 
    item_id2 = query_items(datatotal)

    if confirm_delete.lower() == "yes":
        delete_response = delete_item(item_id2)
        return jsonify({"status": "Item deleted", "delete_response": delete_response})
    else:
        return jsonify({"status": "Deletion not confirmed"}), 400
    
if __name__ == '__main__':
    app.run(debug=True)
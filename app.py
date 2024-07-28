from flask import Flask, request, jsonify, Response
import json
from functions import transform
from about_boards import get_format, get_groups
from bots import fill_data_bot, position_bot, validate_bot
from apis import create, add, modify, search
import time
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db_format = client.get_database("monday-format")

BOARD_IDS = os.getenv("REAL_BOARD_IDS")
BOARD_IDS = json.loads(BOARD_IDS)

event_messages = []

def event_stream():
    global event_messages
    while True:
        if event_messages:
            message = event_messages.pop(0)
            print(f"Event Stream Message: {message}")  # Debug print
            yield f"data: {json.dumps(message)}\n\n"
        time.sleep(1)  # Prevent tight loop, adjust timing as needed


@app.route('/events')
def sse_request():
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/monday-mutation', methods=['POST'])
def handle_item_mutation():
    data = request.get_json()
    print(f"Received data: {data}")  # Debug print

    mutation_type = data.get('mutation_type')
    board_related = data.get('board_related')
    group_related = data.get('group_related')
    values = data.get('values')
    item_name = data.get('item_name')

    response_details = {}  # Dictionary to store all responses

    event_messages.append({'status': 'info', 'message': 'Start mutation flow'})
    print("Mutation flow started")  # Debug print

    board_id = BOARD_IDS.get(board_related)

    event_messages.append({'status': 'info', 'message': 'Getting column format'})
    columns_format = get_format.board_mongo(board_id=board_id, db=db_format, collection=board_related)

    event_messages.append({'status': 'info', 'message': 'Getting board group'})
    board_groups = get_groups.board_mongo(board_id=board_id, db=db_format, collection=board_related)

    event_messages.append({'status': 'info', 'message': 'Filling data'})
    fill_data = fill_data_bot.fill_data_to_columns(columns_format=columns_format, data_input=values)

    event_messages.append({'status': 'info', 'message': 'Finding group'})
    group_id = position_bot.find_group(board_groups, group_related)

    columns, value_update, value_update_found = transform.transform_columns_to_graphql_format(fill_data)

    if mutation_type == 'create':
        event_messages.append({'status': 'info', 'message': 'Creating item'})
        create_response = create.item(board_id=board_id, group_id=group_id['id'], item_name=item_name, column_values=columns)
        response_details['create'] = create_response

    elif mutation_type == 'modify':
        event_messages.append({'status': 'info', 'message': 'Modifying item'})
        item = search.item_summary(collection=board_related, query=f"{item_name} {group_related}")
        match_item = validate_bot.item(search_result=str(item), item_input=f"item name: {item_name}\nboard: {board_related}\ngroup: {group_related}")
        if match_item:
            modify_response = modify.item(item_id=item['id'], board_id=board_id, column_values=columns)
            response_details['modify'] = modify_response
        else:
            print("No exact item found, operation aborted")  # Debug print
            response_details['error'] = 'Can not find exact item to modify, please modify manually.'

    if value_update_found:
        event_messages.append({'status': 'info', 'message': 'Adding an update'})
        update_response = add.update(item_id=item['id'], body=value_update)
        response_details['update'] = update_response
    
    event_messages.append({'status': 'success', 'message': 'Mutation completed'})
    print("Mutation operation completed")  # Debug print

    response_details['message'] = 'Operation completed'
    print(response_details)
    return str(response_details), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7843, debug=True)

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

    event_messages.append({'status': 'info', 'message': 'Start mutation flow'})
    print("Mutation flow started")  # Debug print

    board_id = BOARD_IDS.get(board_related)

    event_messages.append({'status': 'info', 'message': 'Getting column format'})
    columns_format = get_format.board_mongo(board_id=board_id, db=db_format, collection=board_related)
    print(f"Column Format: {columns_format}")  # Debug print

    event_messages.append({'status': 'info', 'message': 'Getting board group'})
    board_groups = get_groups.board_mongo(board_id=board_id, db=db_format, collection=board_related)
    print(f"Board Groups: {board_groups}")  # Debug print

    event_messages.append({'status': 'info', 'message': 'Filling data'})
    fill_data = fill_data_bot.fill_data_to_columns(columns_format=columns_format, data_input=values)
    print(f"Filled Data: {fill_data}")  # Debug print

    event_messages.append({'status': 'info', 'message': 'Finding group'})
    group_id = position_bot.find_group(board_groups, group_related)
    print(f"Group ID: {group_id}")  # Debug print

    columns, value_update, value_update_found = transform.transform_columns_to_graphql_format(fill_data)
    
    response = None
    item_id = ""

    if mutation_type == 'create':
        event_messages.append({'status': 'info', 'message': 'Creating item'})
        response = create.item(board_id=board_id, group_id=group_id['id'], item_name=item_name, column_values=columns)
        item_id = response["data"]["create_item"]["id"] if 'data' in response else None
        print(f"Item created with ID: {item_id}")  # Debug print

    elif mutation_type == 'modify':
        event_messages.append({'status': 'info', 'message': 'Modifying item'})
        item = search.item_summary(collection=board_related, query=f"{item_name} {group_related}")
        
        # validate item search result
        search_item_result = str(item)
        item_input = f"""item name: {item_name}\nboard: {board_related}\ngroup: {group_related}"""
        match_item = validate_bot.item(search_result=search_item_result, item_input=item_input)
        if match_item.lowercase == "true":
            item_id = item['id']
            response = modify.item(item_id=item_id, board_id=board_id, column_values=columns)
        else:
            print("No exact item found, operation aborted")  # Debug print
            return {'message': 'Can not find exact item, please modify manually.'}, 200

    if value_update_found:
        event_messages.append({'status': 'info', 'message': 'Adding an update'})
        add.update(item_id=item_id, body=value_update)
    
    event_messages.append({'status': 'success', 'message': 'Mutation completed'})
    print("Mutation operation completed")  # Debug print

    return {'message': 'Operation completed successfully'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7843)

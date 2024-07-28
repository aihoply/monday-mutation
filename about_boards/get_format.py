import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.monday.com/v2"

headers = {
  'Authorization': os.getenv('MONDAY_API_KEY'),
  'Content-Type': 'application/json'
}

def board(board_id):
    query = f"""
query {{
boards(ids: [{board_id}]) {{
columns(types: [name, text, link, numbers, checkbox, phone, date, status, board_relation, email, item_assignees, person, long_text, people, dropdown]) {{
  title
  type
  id
  settings_str
}}
}}
}}
"""
    response = requests.post(url=url, json={'query': query}, headers=headers)
    return response.json()['data']['boards']['columns']
    
def board_mongo(board_id, db, collection):
    document = db[collection].find_one({})
    cols_format = document['columns format']
    return cols_format

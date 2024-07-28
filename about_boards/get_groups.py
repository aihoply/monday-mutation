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
    name
    groups {{
      id title
    }}
  }}
}}
"""
    response = requests.post(url=url, json={'query': query}, headers=headers)
    return response.json()


def board_mongo(board_id, db, collection):
    document = db[collection].find_one({})
    groups = document['groups']
    return groups

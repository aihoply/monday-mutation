import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.monday.com/v2"

headers = {
  'Authorization': os.getenv('MONDAY_API_KEY'),
  'Content-Type': 'application/json'
}

def update(item_id, body, board_kind="public"):

  url = "https://api.monday.com/v2"
  query = f"mutation {{ create_update (item_id: {item_id}, body: \"{body}\") {{ id }} }}"
  payload = json.dumps({"query": query})
  
  response = requests.request("POST", url, headers=headers, data=payload)

  return response.text
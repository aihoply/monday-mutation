import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.monday.com/v2"

headers = {
  'Authorization': f'{os.getenv('MONDAY_API_KEY')}',
  'Content-Type': 'application/json'
}

def create_update(iditem, body, board_kind="public"):

  url = "https://api.monday.com/v2"
  query = f"mutation {{ create_update (item_id: {iditem}, body: \"{body}\") {{ id }} }}"
  payload = json.dumps({"query": query})
  
  response = requests.request("POST", url, headers=headers, data=payload)

  return response.text
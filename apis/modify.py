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

def item(item_id, board_id, column_values, create_labels_if_missing=True):
    escaped_column_values = json.dumps(column_values)
    mutation = f"""
      mutation {{
        change_multiple_column_values(
          item_id: {item_id}
          board_id: {board_id}
          create_labels_if_missing: false
          column_values: {escaped_column_values}
        ) {{
          id
        }}
      }}
      """
    
    data = {
        "query": mutation
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run with a {response.status_code}: {response.text}")
    
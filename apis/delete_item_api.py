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

def delete_item(item_id):
    # Define the GraphQL mutation with the given item_id
    mutation = f"""
    mutation {{
      delete_item (item_id: {item_id}) {{
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
  
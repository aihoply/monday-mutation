import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.monday.com/v2"

headers = {
  'Authorization': f'{os.getenv('MONDAY_API_KEY')}',
  'Content-Type': 'application/json'
}

import requests

def fetch_boards_in_folder_DAG_Task():
    url = 'https://api.monday.com/v2'
    headers = {
        'Authorization': f'{os.getenv('MONDAY_API_KEY')}',
        'Content-Type': 'application/json'
    }
    query = '''
    query {
        folders(ids: [5816200], limit: 100) {
            id name children {id name type}
        }
    }
    '''
    response = requests.post(url, json={'query': query}, headers=headers)
    if response.status_code == 200:
        return response.json()['data']['folders'][0]['children']
    else:
        print('Failed to fetch data:', response.status_code, response.text)
        return None



# boards = fetch_boards_in_folder_DAG_Task()

# # Process the boards to remove numbers from the names and create a dictionary
# board_dict = {}
# for board in boards:
#     if board['type'] == 'board':  # Ensure we're only processing boards
#         clean_name = ' '.join(part for part in board['name'].split() if not part.isdigit())
#         board_dict[clean_name] = board['id']

# # Save to JSON file
# with open('board_ids.json', 'w') as json_file:
#     json.dump(board_dict, json_file, indent=2)

# print("Boards have been processed and saved to 'board_ids.json'")
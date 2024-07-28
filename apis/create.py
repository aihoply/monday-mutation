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

def item(board_id, item_name, column_values, group_id=None):
    # Ensure column_values is a properly escaped JSON string
    escaped_column_values = json.dumps(column_values)  # Escape the JSON string correctly

    # Create the mutation query string based on the presence of group_id
    if group_id:
        query = f"""
        mutation {{
          create_item (
            board_id: {board_id},
            group_id: "{group_id}",
            item_name: "{item_name}",
            column_values: {escaped_column_values}
          ) {{
            id
          }}
        }}
        """
    else:
        query = f"""
        mutation {{
          create_item (
            board_id: {board_id},
            item_name: "{item_name}",
            column_values: {escaped_column_values}
          ) {{
            id
          }}
        }}
        """
    
    # print(query)  # Output the complete query for debugging
    response = requests.post(url, headers=headers, json={'query': query})
    return response.json()  # Parse the JSON response

# Example usage
# new_item = item(
#     board_id=1882419362,
#     group_id="new_group12999__1",
#     item_name="Nguyen Van B",
#     column_values=json.dumps({  # Convert the dictionary to a JSON string
#         "name": "Nguyen Van B",
#         "group_id": "C GROUP",
#         "code": "NVC",
#         "text": "Anh C",
#         "priority": "High",
#         "phone_1": "03876238221",
#         "email": {
#             "text": "nguyenc@aihoply.com",
#             "email": "nguyenc@aihoply.com"
#         },
#         "connect_boards5": {
#             "item_ids": ["1886088965"]
#         }
#     })
# )

# print(new_item)
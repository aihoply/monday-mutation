import requests
import json
import os

# constants
API_KEY = f'{os.getenv('MONDAY_API_KEY')}',
API_URL = "https://api.monday.com/v2"
WORKSPACE_ID = 556136
# headers
headers = {"Authorization": API_KEY, "API-Version": "2023-04"}

class MutationMondayApi:
    def __init__(self):
        self.api_key = API_KEY
        self.api_url = API_URL
        self.headers = headers
    
    def make_New_Workspace(self, name):
        # this funciotn will create a new workspace
        # name: the name of the workspace

        query = "mutation { create_workspace (name: " + name + " , kind: open) { id name } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
    def make_New_Folder_In_Workspace(self, name, workspace_id):
        # this function will create a new folder in a workspace, the folder will be created in the root of the workspace
        # name: the name of the folder
        # workspace_id: the id of the workspace in which the folder will be created

        query = "mutation { create_folder (name: " + name + " , workspace_id: " + workspace_id + ") { id name } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
    def make_New_Board(self, name):
        # this function will create a new board in the root of the workspace
        # name: the name of the board

        query = "mutation { create_board (name: " + name + ") { id name } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
    def make_New_Board_In_Folder(self, name, folder_id):
        # this function will create a new board in a folder
        # name: the name of the board
        # folder_id: the id of the folder in which the board will be created

        query = "mutation { create_board (name: " + name + " , folder_id: " + folder_id + ") { id name } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
    def make_New_Group_In_Board(self, name, board_id):
        # this function will create a new group in a board
        # name: the name of the group
        # board_id: the id of the board in which the group will be created

        query = "mutation { create_group (board_id: " + board_id + " , name: " + name + ") { id title } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
    def make_New_Item_In_Group(self, name, group_id):
        # this function will create a new item in a group
        # name: the name of the item
        # group_id: the id of the group in which the item will be created

        query = "mutation { create_item (group_id: " + group_id + " , name: " + name + ") { id name } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
    def make_New_Column_In_Board(self, board_id, title, column_type):
        # this function will create a new column in a board
        # board_id: the id of the board in which the column will be created
        # title: the title of the column
        # column_type: the type of the column

        query = "mutation { create_column (board_id: " + board_id + " , title: " + title + " , type: " + column_type + ") { id title } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
    def make_New_Column_In_Group(self, group_id, title, column_type):
        # this function will create a new column in a group
        # group_id: the id of the group in which the column will be created
        # title: the title of the column
        # column_type: the type of the column

        query = "mutation { create_column (group_id: " + group_id + " , title: " + title + " , type: " + column_type + ") { id title } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
    def make_New_item_In_Board(self, board_id, group_id, item_name, column_values):
        group_query = ""
        if group_id:
            group_query = f"group_id: {group_id}"
        query = f"""
mutation {{
  create_item(
    item_name: {item_name}
    board_id: {board_id}
    {group_query}
    column_values: {column_values}
  ) {{
    id
    name
    board {{
      name
    }}
    group {{
      title
    }}
    column_values {{
      id
      value
    }}
  }}
}}
"""
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
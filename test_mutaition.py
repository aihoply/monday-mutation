# make an API request to the Monday.com API to get the board ID for the board
# that we want to work with

import requests
import json
import sys

# constants
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjM3NTY2ODU2NywiYWFpIjoxMSwidWlkIjo1NjQ0MzEwNiwiaWFkIjoiMjAyNC0wNi0yNFQwMjo1NToxOC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTY5OTg3OTQsInJnbiI6ImFwc2UyIn0.jr1e5kt-qQPIdBFZidO54d3_Fsn5pkyjiCFKWRlHPvk"
API_URL = "https://api.monday.com/v2"
WORKSPACE_ID = 556136
# headers
headers = {"Authorization": API_KEY, "API-Version": "2023-04"}

# [boards]
contactID = 1882419362
businessID = 1882419811
general_admin_tasksID = 1882420292
individual_tax_returnID = 1882420822
company_tax_and_frID = 1882420947
trust_tax_and_frID = 1882421025
partnership_taxID = 1882421120
smsf_tax_and_frID = 1882421162
quarterly_basID = 1882421850
monthly_iasID = 1882421905
payrollID = 1882421947
tpar_lodgementID = 1882422096

class MutationMondayApi:
    def __init__(self):
        self.api_key = API_KEY
        self.api_url = API_URL
        self.headers = headers

    def get_id_of(self, entity, name):
        # this function will return the id of the item with the given name
        # name: the name of the item

        query = "query { items_by_column_values (board_id: 556136, column_id: name, column_value: " + name + ") { id } }"
        response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
        return response.json()
    
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
        
    
class QueryMondayApi:
    def __init__(self):
        self.api_key = API_KEY
        self.api_url = API_URL
        self.headers = headers
    
    @staticmethod
    def get_board_columns(board_id):
        query = f"""
query {{
  boards(ids: [{board_id}]) {{
    name
    groups {{
      id
      title
      items_page {{
        cursor
        items {{
          id
          name
          column_values {{
            id
            value
          }}
        }}
      }}
    }}
    columns(types: [name, text, link, numbers, checkbox, phone, date, status, board_relation, email, item_assignees, person, long_text, people, dropdown]) {{
      title
      type
      id
      settings_str
    }}
  }}
}}
"""
        response = requests.post(API_URL, json={'query': query}, headers=headers)
        return response.json()

# print(QueryMondayApi.get_board_columns(1802112856))

# def main():
#     # create an instance of the class
#     mutation_api = MutationMondayApi()

#     # create a new workspace
#     # response = mutation_api.make_New_Workspace("My Workspace")
#     # print(response)

#     # create a new folder in the workspace
#     # response = mutation_api.make_New_Folder_In_Workspace("My Folder", "1")
#     # print(response)

#     # create a new board in the root of the workspace
#     # response = mutation_api.make_New_Board("My Board")
#     # print(response)

#     # # create a new board in a folder
#     # response = mutation_api.make_New_Board_In_Folder("My Board", "1")
#     # print(response)

#     # # create a new group in a board
#     # response = mutation_api.make_New_Group_In_Board("My Group", "1")
#     print(response)

#     # # create a new item in a group
#     # response = mutation_api.make_New_Item_In_Group("My Item", "1")
#     # print(response)

#     # # create a new column in a board
#     # response = mutation_api.make_New_Column_In_Board("1", "My Column", "text")
#     # print(response)

#     # # create a new column in a group
#     # response = mutation_api.make_New_Column_In_Group("1", "My Column", "text")
#     # print(response)
    
# # main()
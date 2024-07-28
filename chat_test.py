from openai import OpenAI
from pymongo import MongoClient
import configparser
import multiprocessing
import json
import time
from test_mutaition import QueryMondayApi, MutationMondayApi
from bots.fill_data_bot import fill_data_to_columns
# from mutationFunction import createitem,send_graphql_request,createupdate,delete_item
import requests
import os
import time

gpt = OpenAI(
  organization='org-B3G3LCdxIpyHlWLBtXdigJap',
  api_key= "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",
  project="proj_A2ZNgbdF5Svunv3V1rALJLpn"
)


ASSISTANT_ID = "asst_xeFIiEvATHACS5kUdMRRbker"
GLOBAL_THREAD_ID = ""

old_tools = [
{
  "type": "function",
  "function": {
    "name": "get_board_cloumns",
    "description": "Get the cloums of a board to see what column are in that board to make specifict input, then process next mutation step. If user not mention board name, ask user.",
    "parameters": {
      "type": "object",
      "properties": {
        "board_name": {
          "type": "string",
          "description": "The name of the board. enum: ['contact', 'business', 'general_admin_tasks', 'individual_tax_return', 'individual_tax_return', 'company_tax_and_fr', 'trust_tax_and_fr', 'partnership_tax', 'smsf_tax_and_fr', 'quarterly_bas', 'monthly_ias', 'payroll', 'tpar_lodgement']",
        }
      },
      "required": ["board_name"],
    },
  }
},
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "monday_mutation_item",
            "description": """This function performs an action on the Monday.com platform such as creating, modifying, or deleting an item.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "mutation_type": {
                        "type": "string",
                        "enum": ["create", "modify", "delete"]
                    },
                    "item_name": {
                        "type": "string",
                        "description": "The name of the item, which could be anything such as an action, name, etc.",
                    },
                    "board_related": {
                        "type": "string",
                        "enum": ['Contact List', 'Business List', 'FBT Employee Contribution', 'Quarterly BAS', 'SMSF Tax and FR', 'Company Tax and FR', 'Individual Tax Return', 'General Admin Task', 'Monthly IAS', 'TPAR Lodgement', 'Annual BAS', 'Payroll', 'Partnership Tax', 'Trust Tax and FR'],
                        "description": "Name of the board the item place in.",
                    },
                    "group_related": {
                        "type": "string",
                        "description": "The group to which the item belongs. Group name often comes after the board name, e.g., 'Individual tax return 2023' where '2023' is the group. If the user does not specify a group, set to 'default'.",
                    },
                    "values": {
                        "type": "json_object",
                        "description": "A JSON object as a string containing column names and input values based on user query. Example values: name, connect item (business, contact, task, etc.), person, assignee, phone, address, TFN, status, priority, note",
                    },
                    "update": {
                        "type": "string",
                        "description": "If the user wants to add or create an update for the item, write the update content here. Mention a person with @, e.g., @Phong Dam.",
                    }
                },
                "required": ["mutation_type", "item_name", "board_related", "group_related", "values"],
            },
        }
    }
]

# Make a new contact item, name it Vo Nhat Truong, phone 0867949312, he lives in America, tfn is 123 713 193, tell me if you create success
# Make a new item 

BOARD_IDS = {
  "Quarterly BAS": "1802369311",
  "Payroll": "1802383712",
  "Company Tax and FR": "1802383765",
  "Trust Tax and FR": "1802383793",
  "SMSF Tax and FR": "1802383803",
  "Partnership Tax": "1802690144",
  "Individual Tax Return": "1802690190",
  "Monthly IAS": "1802984917",
  "TPAR Lodgement": "1806574164",
  "General Admin Task": "1835869988",
  "Annual BAS": "1859804144",
  "FBT Employee Contribution": "1859804845",
  "Contact list": "1875075592",
  "Business list": "1875076582",
}

def monday_mutation_item(mutation_type, board_related, values, item_name, group_related, update=""):
  print(mutation_type)
  if mutation_type == "create":
    url = "http://localhost:5000/create-item"
    headers = {"Content-Type": "application/json"}
    payload = {
        "mutation_type": mutation_type,
        "board_related": board_related,
        "group_related": group_related,
        "values": values,
        "item_name": item_name
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        response_data = response.json()
        print(response_data)
    except json.JSONDecodeError:
        print("Failed to decode JSON from response:", response.text)

  elif mutation_type == "modify":
    url = "http://localhost:5000/modify-item"
    headers = {"Content-Type": "application/json"}
    payload = {
        "board_related": board_related,
        "group_related": group_related,
        "values": values
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        response_data = response.json()
        print(response_data)
    except json.JSONDecodeError:
        print("Failed to decode JSON from response:", response.text)
  elif mutation_type == "delete":
   url = 'http://127.0.0.1:5000/delete-item'
   check=input("Bạn có thật sự muốn delete item không Yes or No: ")
   data = {
      "board_related": board_related,
      "values": values,
      "confirm_delete": check  
  }
  response = requests.post(url, json=data)
  print(response.json())

  return "Item created successful"

def get_board_columns(board_name):
    board_id = BOARD_IDS.get(board_name)
    if board_id is not None:
        
        columns_data = QueryMondayApi.get_board_columns(board_id=board_id)
        print("done get board column")
        instruction = f"""
        Insert your value in each columns, if there is no data just leave it "none". it should be like this:
        {
            "title": "Business",
            "type": "board_relation",
            "id": "contact_account",
            "value": *insert value here*,
        }
        here are the columns of board {board_name}
        {columns_data}
        """
        print(instruction)
        return instruction
    else:
        return "Invalid board name"


def calling_function_parallel(func_list):
    results = []
    for d in func_list:
        result = call_function_by_name_with_args(d['name'], d['arguments'], d['tool_call_id'])
        results.append(result)
    return results


def call_function_by_name_with_args(func_name, args_json, tool_call_id):
    args = json.loads(args_json)
    if func_name in globals() and callable(globals()[func_name]):
        output = globals()[func_name](**args)
        return {"tool_call_id": tool_call_id, "output": output}
    else:
        return {"tool_call_id": tool_call_id, "output": f"Function '{func_name}' not found."}



def handle_function_call_event(event):
  actions = event.data.required_action.submit_tool_outputs.tool_calls
  func_list = []
  for action in actions:
    if action.type == 'function':
      function_name = action.function.name
      function_args = action.function.arguments
      call_id = action.id
      function_item = {
        "name": function_name,
        "arguments": function_args,
        "tool_call_id": call_id
      }
      func_list.append(function_item)
  print(func_list)
  file_path = os.path.join(os.getcwd(), "temp.txt")
  with open('./temp.txt', 'w') as fi:
        fi.write(json.dumps(func_list, indent=4))
        print("Đã lưu")
  tool_ouputs = calling_function_parallel(func_list)
  return tool_ouputs


def process_stream(stream, parent_thread_id=None):
  global GLOBAL_THREAD_ID
  thread_id = '' if parent_thread_id is None else parent_thread_id
  run_id = ''
  for event in stream:
    event_type = event.event

    """DEBUG PRINTS"""
    # if event_type != 'thread.message.delta':
    #   print('\n', event_type)
    
    if event_type == 'thread.created':
      thread_id = event.data.id
      GLOBAL_THREAD_ID = thread_id
    if event_type == 'thread.run.requires_action':
      run_id = event.data.id
    process_event(event, thread_id, run_id)


def process_event(event, thread_id='', run_id=''):
  event_type = event.event
  
  if event_type == 'thread.run.requires_action':
    tool_outputs = handle_function_call_event(event)
    run_after_function_calling = gpt.beta.threads.runs.submit_tool_outputs(
      thread_id=GLOBAL_THREAD_ID,
      run_id=run_id,
      tool_outputs=tool_outputs,
      stream=True
    )
    process_stream(run_after_function_calling, parent_thread_id=GLOBAL_THREAD_ID)
    # return 'function_called', tool_outputs
  
  elif event_type == 'thread.message.delta':
    message_content = event.data.delta.content[0].text.value
    print(message_content, end="", flush=True)
    # return 'message_printed', 'x'
  
  # else:
    # return event_type, 'x'
    # print(event_type)


def creat_new_conversation(query):
  stream = gpt.beta.threads.create_and_run(
    thread={
        "messages": [
            {"role": "user", "content": query},
        ]
    },
    assistant_id=ASSISTANT_ID,
    tools=tools,
    stream=True
  )
  save_input=query
  return stream


def add_message_to_thread(thread_id, message):
  gpt.beta.threads.messages.create(
    thread_id,
    role = "user", 
    content = message
  )


def run_gpt():
  stream = gpt.beta.threads.runs.create(
    thread_id=GLOBAL_THREAD_ID,
    assistant_id=ASSISTANT_ID,
    tools=tools,
    stream=True
  )
  return stream


import time
if __name__ == '__main__':
  input_text = input("Enter your message: ")
  with open("./promt.txt",'w',encoding='utf-8') as fo:
    fo.write(input_text) 
  stream = creat_new_conversation(input_text)
  
  start = time.time()

  print("\nAssistant...\n")
  
  process_stream(stream)  
  
  print("\nDone!")
  print("Time taken:", time.time() - start)
  while True:
    input_text = input("Enter your message: ")
    with open("./promt.txt",'w',encoding='utf-8') as fo:
       fo.write(input_text) 
    add_message_to_thread(GLOBAL_THREAD_ID, input_text)
    stream = run_gpt()
    start = time.time()
    print("\nAssistant...\n")
    process_stream(stream)  
    print("\nDone!")
    print("Time taken:", time.time() - start)
    

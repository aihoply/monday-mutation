import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openai import OpenAI
import json
from apis.search import item_summary
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')
ORG_ID = os.getenv('ORG_ID')
PROJECT_ID = os.getenv('PROJECT_ID')

client = OpenAI(
  organization= f"{ORG_ID}",
  api_key= f"{OPENAI_KEY}",
  project= f"{PROJECT_ID}",
)

tools = [
{
    "type": "function",
    "function": {
        "name": "search_item_id",
        "description": "Searches for and retrieves the unique identifier (ID) of an item within a specified collection on the Monday.com platform based on a given query.",
        "parameters": {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "string",
                    "enum": [
                        "Contact List", 
                        "Business List", 
                        "FBT Employee Contribution", 
                        "Quarterly BAS", 
                        "SMSF Tax and FR", 
                        "Company Tax and FR", 
                        "Individual Tax Return", 
                        "General Admin Task", 
                        "Monthly IAS", 
                        "TPAR Lodgement", 
                        "Annual BAS", 
                        "Payroll", 
                        "Partnership Tax", 
                        "Trust Tax and FR"
                    ],
                    "description": "The name of the collection where the item is located. Must be one of the predefined types such as 'Company Tax and FR'."
                },
                "query": {
                    "type": "string",
                    "description": "The query string used to describe and locate the item, such as 'Gentile constructions 2023'."
                }
            },
            "required": ["collection", "query"]
        }
    }
}
]


def search_item_id(collection, query):
    return str(item_summary(collection, query))


def fill_data_to_columns(columns_format, data_input):
    messages = [
        {"role": "system", "content": 
"""
You are a JSON bot have a mission to fill data to a form and return JSON object.

### Instructions:

1. **Review Column Formatting**: Identify required fields and ensure data is accurate and appropriately formatted.

2. **Convert Language and Address**: Translate any non-English text to English.

3. **Check User Requirements**: Understand the user's intent and identify the necessary data. Ensure all required columns are populated based on user input.

4. **Exclude Non-corresponding Data**: Remove any columns without relevant data.

5. **Secondary Column Check**: Handle secondary columns appropriately, excluding those with no corresponding data.

6. **Label State Check**: Verify and normalize label states for consistency in case sensitivity, ensuring accurate data handling.

8. **Date Formatting**: Format date columns in JSON as per the specified format, ensuring proper date and time representation in UTC (send the date as a string in YYYY-MM-DD format).

10. **Return JSON Object**: Compile and return the final formatted JSON object, ensuring it meets all specified requirements.

### Instruction About Column Types:

- **connect_board**: 
    + if you want to fill the connect_board value, you must find the id of the item in the board that connect
    + use the function search_item_id, then validate the search result, if the search not match just don't fill it, only fill if the result is match
    + if want to connect more than 1 item, then find as much id as you want
    + example answer: 'value': [123456], 'value': [123456, 654321],...
     
- **update**:
    + if user want to add an update message, add a "update" field with value, do not create this field if there is no update message

- **status**: 
    + when chose the label remember it is case sensitive
    + only chose the label from the label list in it setting_str
    + don't generate label

your output should look like this:
"data": {
    "columns": [
        {
        "title": "some title",
        "type": "some type",
        "id": "unique_id_ 1",
        "value": "some value"
        },
        {
        "title": "some title",
        "type": "some type",
        "id": "unique-id_2",
        "value": "some value"
        },
        {
        "title": "some title",
        "type": "group",
        "id": "unique_id_3",
        "value": "some value"
        }
        //...other columns
    ],
    "update" : "some update message if user have any"
}
"""},
        {"role": "user", "content": 
f"""
### Columns format:
{str(columns_format)}

### Values (only use these value to make decision):
{str(data_input)}

### Filled column values:
"""}
        ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        response_format={ "type": "json_object" },
        temperature=0,
        tools=tools,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {
            "search_item_id": search_item_id,
        }
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                collection=function_args.get("collection"),
                query=function_args.get("query"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        second_response_message = second_response.choices[0].message.content
        return second_response_message

    response_message = response.choices[0].message.content
    return response_message


# example:
# item = item_summary("Company Tax and FR", "Gentile constructions 2023")
# print("Item:", item)
# Item: {'collection': 'Company Tax and FR', 'group_title': '2022', 'id': '1802670873', 'name': 'GENTILE CONSTRUCTIONS PTY LTD'}

# from about_boards import get_format
# column_format = get_format.board(123)

# data_input = "{\"name\": \"Nguyen Van C\", \"group ID\": \"C GROUP\", \"Code\": \"NVC\", \"prefered name\": \"Anh C\", \"prioty\": \"high\", \"phone\": \"03876238221\", \"email\": \"nguyenc@aihoply.com\", \"connect business\": \"Van B Limited\"}, \"update message\": \"prepare for tomorow meeting @Truong Vo\"}"


# fill_data_to_columns(columns_format=column_format, data_input=data_input)
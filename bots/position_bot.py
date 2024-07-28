from openai import OpenAI
import json
import os
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

def find_group(board_groups, data_input):
    messages = [
        {"role": "system", "content": 
"""
You are a JSON bot have a mission to chose the right group and return the group_id value.
### Instructions:

1. **View All Groups id and title**: Identify all group in the board and the meaning of it.

2. **Read The Input**: Read Input to understand user intent.

3. **Chose The Right Group**: Which group should the item belong to.

4. **Return The Group id**: Only return the id of the group.

your answer should look like this:
{"id": "some_thing_id"}
"""},
        {"role": "user", "content": 
f"""
### Board's Group:
{str(board_groups)}

### Data input:
{str(data_input)}
"""}
        ]
    # print('start find group')
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        response_format={ "type": "json_object" },
        temperature=0
    )
    # print('finish find group!')
    response_message = response.choices[0].message.content
    return json.loads(response_message)

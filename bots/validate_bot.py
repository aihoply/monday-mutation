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

def item(search_result, item_input):
    messages = [
        {"role": "system", "content": 
"""
Your mission is to validate if the search result is the item we looking for, only answer is "true" or "false".
"""},
        {"role": "user", "content": 
f"""
### Searching for:
{str(item_input)}

### Search result:
{str(search_result)}
"""}
        ]
    # print('start find group')
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    # print('finish find group!')
    response_message = response.choices[0].message.content
    return response_message

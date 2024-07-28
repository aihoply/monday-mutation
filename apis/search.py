import requests
from dotenv import load_dotenv

load_dotenv()

def item_summary(collection, query):
    url = "https://dagapis.aihoply.com/api/v1/search_id"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "collection": collection,
        "query": query
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        print(json_response)
        # Assuming the ID is stored in the path `['document']['id']`
        if 'document' in json_response:
            item = json_response['document']
            return item

        else:
            return json_response
    else:
        return "Error: " + str(response.status_code)


# Example usage:
# item = item_summary("Company Tax and FR", "Gentile constructions 2028")
# print("Item:", item)
# Item: {'collection': 'Company Tax and FR', 'group_title': '2022', 'id': '1802670873', 'name': 'GENTILE CONSTRUCTIONS PTY LTD'}
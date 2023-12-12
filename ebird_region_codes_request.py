import requests
import json

extracted_data = []


url = "https://api.ebird.org/v2/ref/region/list/subnational2/US-NY"


headers = {'Content-Type': 'application/json'}
params = {
            "key": "gqrrpnl833pv" 

            }

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    extracted_data.extend(data)

except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")
    # Used ChatGPT for error handling

print(extracted_data)
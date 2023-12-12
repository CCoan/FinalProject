#uses iNaturalist API name search feature to check if GT garden names match named places on the app

import requests
import json
import csv
import re
import time 


csv_file_name = "GreenThumb_Garden_Info_20231129.csv"
name_column = "gardenname"
garden_names = []

#function to remove parentheses and extra white space from garden names 
def remove_parentheses_and_whitespace(text):
    text_without_parentheses = re.sub(r'\([^)]*\)', '', text)
    cleaned_text = ' '.join(text_without_parentheses.split())
    
    return cleaned_text 


with open(csv_file_name, 'r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
            garden_name = row[name_column]
            garden_name_without_parentheses = remove_parentheses_and_whitespace(garden_name)
            garden_names.append(garden_name_without_parentheses)#adding names to list 



url = "https://api.inaturalist.org/v1/places/autocomplete"

first_iteration = True #use to determine if csv file opens in write mode or append mode 
delay_duration=1 #slowing down code to follow iNaturalists instructions of no more that 60 requests per minute 

for garden_name in garden_names:
    headers = {'Content-Type': 'application/json'}
    params = {'q': f"{garden_name}"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()

        # Determine the file mode based on the first_iteration flag
        file_mode = 'w' if first_iteration else 'a'

        # Writing the JSON data to a file named "iNaturalist_name_data.json"
        with open("iNaturalist_name_data.json", file_mode) as json_file:
            json.dump(data, json_file, indent=2)
            json_file.write(',\n')

        # Set the first_iteration flag to False after the first iteration
        first_iteration = False
        time.sleep(delay_duration)

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")




csv_file_path = 'iNaturalistGardens.csv'
csv_file = open(csv_file_path, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id', 'name','latitude','longitude'])


with open('iNaturalist_name_data.json', 'r') as file:
    data_list = json.load(file)

# retrieving results if any of each name search request 
for entry in data_list:
    results_list = entry.get('results', [])  # Get the 'results' list or an empty list if not present
    for result in results_list:
        # Extract latitude and longitude from the "location" field
        latitude, longitude = map(float, result['location'].split(','))

        # Checking if NYC location 
        if latitude >= 40 and -73 >= longitude >= -75:
            csv_writer.writerow([result['id'], result['name'],latitude,longitude]) 
            
csv_file.close()
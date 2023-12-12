import requests
import json
import csv
import time 
import os 
from json.decoder import JSONDecodeError 

###uses coordinates from CGs to search recent nearby observations (past 30 days) 

extracted_data=[]
all_headers = ["Common Name", "Observation Date", "Number Observed", "Latitude", "Longitude"]
json_file_path = "GreenThumb Garden Info_20231209.geojson"

try:
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

        for feature in data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            gardenname = properties.get('gardenname', 'N/A')
            gardenname = gardenname.replace('/', '_') #fixing issue that was causing one garden name to be read as a file path
            coordinates = geometry.get('coordinates',[])
            total_lat = 0
            total_lon = 0
            num_coordinates=len(coordinates[0][0]) 
            for pair in coordinates[0][0]:
                lat=pair[1]
                lon=pair[0]
                total_lat += lat
                total_lon += lon   #had much difficulty accessing all the lat/lon values correctly bc they were inside many nested lists
            avg_latitude = total_lat / num_coordinates 
            avg_longitude = total_lon / num_coordinates
            
            url = f"https://api.ebird.org/v2/data/obs/geo/recent?lat={avg_latitude}&lng={avg_longitude}"
            headers = {'Content-Type': 'application/json'}
            output_files=[]

            params = {
                "key": "gqrrpnl833pv",
                "back":"30",
                "dist":".03"
                }

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()

                bird_data = response.json()

                if bird_data:
                    for entry in bird_data:
                        common_name=entry.get("comName", "N/A")
                        obs_date=entry.get("obsDt","N/A")
                        obs_number=entry.get( "howMany","N/A")
                        latitude=entry.get("lat","N/A")
                        longitude=entry.get("lng","N/A")

                        extracted_data.append({
                            "Common Name": common_name,
                            "Observation Date": obs_date,
                            "Number Observed": obs_number,
                            "Latitude": latitude,
                            "Longitude": longitude
                            })
                    
                else:
                    print(f"No data returned for Latitude: {avg_latitude}, Longitude: {avg_longitude}")
            except requests.exceptions.RequestException as e:
                print(f"Error making request for Latitude: {avg_latitude}, Longitude: {avg_longitude}: {e}")




except FileNotFoundError:
    print(f"Json file not found: {json_file_path}")
except JSONDecodeError as json_error:
    print(f"Error decoding JSON file: {json_error}")
except Exception as e:
    print(f"Other error reading JSON file: {e}")


with open("res/ebird_recent_observations.csv", 'w', newline='') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=all_headers)


    csv_writer.writeheader()


    csv_writer.writerows(extracted_data)
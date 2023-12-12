#calculates avg coordinates from Greenthumb's perimeter coordinates and writes them to a csv file (to be uploaded to google maps)

import json
import csv
import requests
from json.decoder import JSONDecodeError #used chatgpt for error handling

garden_coordinates={} #empty dictionary to store coordinates 

json_file_path = "GreenThumb Garden Info_20231129.geojson"  ###uses coordinates from CGs in Greenthumb file

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
            #use total_lat and total_lon to calculate averages    
            avg_latitude = total_lat / num_coordinates
            avg_longitude = total_lon / num_coordinates
            garden_coordinates.update({gardenname: [avg_latitude, avg_longitude]})  #adding name and avg coordinates to dictionary          

except FileNotFoundError:
    print(f"Json file not found: {json_file_path}")
except JSONDecodeError as json_error:
    print(f"Error decoding JSON file: {json_error}")
except Exception as e:
    print(f"Other error reading JSON file: {e}")

#write name and avg coordinates to a csv file
csv_garden_file_name = "res/garden_coordinates.csv"
with open(csv_garden_file_name, 'w', newline='') as garden_csv_file:
    csv_writer = csv.writer(garden_csv_file)
    csv_writer.writerow(['Garden Name', 'Latitude', 'Longitude'])

    for garden_name, coordinates in garden_coordinates.items():
        csv_writer.writerow([garden_name, coordinates[0], coordinates[1]])
#uses GT file to get avg garden coordinates; stores in dictionary; checks ebird files for nearby observations 2019 or later
#figure out a fix so that birds with exact same coordinates are plottable on map?
#make new csv file once at 2000 entries? 

import requests
import json
import csv
from datetime import datetime
import random
from math import *
from json.decoder import JSONDecodeError 



garden_coordinates={}

json_file_path = "GreenThumb Garden Info_20231209.geojson"  ###uses coordinates from CGs in Greenthumb file

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
            garden_coordinates.update({gardenname: [avg_latitude, avg_longitude]}) #add garden name and average coordinates to dictionary 

           

except FileNotFoundError:
    print(f"Json file not found: {json_file_path}")
except JSONDecodeError as json_error:
    print(f"Error decoding JSON file: {json_error}")
except Exception as e:
    print(f"Other error reading JSON file: {e}")

def great_circle_distance(coordinates1, coordinates2): #this function and the one below were taken from a stack overflow post I found through googling how to check if coordinates are in certain range of each other 
  latitude1, longitude1 = coordinates1
  latitude2, longitude2 = coordinates2
  d = pi / 180  # factor to convert degrees to radians
  return acos(sin(longitude1*d) * sin(longitude2*d) +
              cos(longitude1*d) * cos(longitude2*d) *
              cos((latitude1 - latitude2) * d)) / d

def in_range(coordinates1, coordinates2, range):
  return great_circle_distance(coordinates1, coordinates2) < range

file_paths=['ebd_US-NY-085_relOct-2023.txt','ebd_US-NY-081_relOct-2023.txt','ebd_US-NY-061_relOct-2023.txt','ebd_US-NY-047_relOct-2023.txt','ebd_US-NY-005_relOct-2023.txt']
for file_path in file_paths:
    borough_code=file_path.split('-')[2][:3]
    csv_file_name_base = f"res/ebird_garden_observations_{borough_code}"
    csv_file_name = f"{csv_file_name_base}_1.csv"
    row_count = 0 #counting rows and starting new file at 2000 rows bc Google maps only accepts 2000 rows or fewer per file

    with open(csv_file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Observation Date', 'Number Observed', 'Common Name',"Latitude","Longitude"])

        
        with open(file_path, 'r') as ebird_csv_file:
            csv_reader = csv.DictReader(ebird_csv_file, delimiter='\t')

            for row in csv_reader:
                observation_date_str = row['OBSERVATION DATE']
                bird_latitude = float(row['LATITUDE'])
                bird_longitude = float(row['LONGITUDE'])
                

                try:
                    observation_date = datetime.strptime(observation_date_str, "%Y-%m-%d")
                except ValueError:
                    print(f"Skipping row due to invalid date format: {observation_date_str}")
                    continue
                #(Used ChatGPT for help handling older data in diff format)
                # Checking if coordinates are close and the year is 2019 or later
                for entry in garden_coordinates:
                    garden_latitude, garden_longitude = garden_coordinates[entry]
                    

                    if in_range((garden_latitude, garden_longitude), (bird_latitude, bird_longitude), 0.0003) and observation_date.year >= 2022:
                        print(f"Match found for {entry} in {file_path}")
                        bird_name = row['COMMON NAME']
                        date_observed = row['OBSERVATION DATE']
                        observation_number=row['OBSERVATION COUNT']
                        
                        #not ideal solution but trying to slightly vary coordinates so they don't all show up on top of each other on a map
                        random_add_or_subtract_lat = 1 if random.choice([True, False]) else -1 
                        random_add_or_subtract_lon = 1 if random.choice([True, False]) else -1
                        random_variation_lat = random.uniform(0.000001, 0.000009)*random_add_or_subtract_lat
                        random_variation_lon = random.uniform(0.000001, 0.000009)*random_add_or_subtract_lon
                        adjusted_lat = bird_latitude + random_variation_lat
                        adjusted_lon = bird_longitude + random_variation_lon
                        

                        
                        csv_writer.writerow([date_observed,observation_number, bird_name, adjusted_lat, adjusted_lon])
                        row_count += 1

                        if row_count == 2000:
                            # Close the current file and open a new one
                            #didn't use "with open" here bc it was causing an error message about operations on a closed file and couldn't figure out how to fix 
                            new_csv_file_name = f"{csv_file_name_base}_2.csv"
                            new_csvfile = open(new_csv_file_name, 'w', newline='')
                            csv_writer = csv.writer(new_csvfile)  
                            csv_writer.writerow(['Observation Date', 'Number Observed', 'Common Name', "Latitude", "Longitude"])
                            row_count = 0


new_csvfile.close()

    


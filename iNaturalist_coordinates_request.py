#add number of observed to data extracted? 

import requests
import json
import csv
import time 
import os 
from json.decoder import JSONDecodeError 


url = "https://api.inaturalist.org/v1/observations/"
headers = {'Content-Type': 'application/json'}
delay_duration=1
json_file_path = "GreenThumb Garden Info_20231209.geojson"
output_files=[]


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
 

            params = {
              "year":["2019","2020","2021","2022","2023"],
              "identifications":"most_agree", #other users mostly agree w original users ID
              "captive":"false", #excludes domestic animals/non-wild garden plants etc. 
              "lat":f"{avg_latitude}",
              "lng":f"{avg_longitude}",
              "radius":".03"#must be this radius (km) around given coordinates
            }
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()

                iNaturalist_data = response.json()

                if iNaturalist_data.get('results'):
                    new_json_file_path = f"res/iNaturalist_garden_obs_{gardenname}.json"
                    output_files.append(new_json_file_path)
                    with open(new_json_file_path, 'w') as new_json_file:
                        json.dump(iNaturalist_data, new_json_file, indent=2)
                else:
                    print(f"No data returned for Latitude: {avg_latitude}, Longitude: {avg_longitude}")

            except requests.exceptions.RequestException as e:
                print(f"Error making request for Latitude: {avg_latitude}, Longitude: {avg_longitude}: {e}")
            time.sleep(delay_duration)

except FileNotFoundError:
    print(f"Json file not found: {json_file_path}")
except JSONDecodeError as json_error:
    print(f"Error decoding JSON file: {json_error}")
except Exception as e:
    print(f"Other error reading JSON file: {e}")
    

taxons=["Amphibia","Arachnida","Aves","Fungi","Mammalia","Insecta","Mollusca","Reptilia","Plantae"]

for taxon in taxons:
    csv_file_name = f"res/iNaturalist_garden_observations_{taxon}.csv"


    with open(csv_file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Garden Name', 'Observation Date', 'Taxonomy', 'Preferred Common Name',"Latitude","Longitude"])

    # Processing each of the JSON files created in previous step
        for output_file in output_files:
            new_json_file_path = output_file

            with open(new_json_file_path, 'r') as json_file:
                json_data = json.load(json_file)

                if json_data.get('results'):
                    for result in json_data['results']:
                        gardenname = os.path.splitext(os.path.basename(new_json_file_path))[0].split('_')[-1]#trying to extract garden name from file path
                        date = 'N/A'
                        iconic_taxon_name = 'N/A'
                        preferred_common_name = 'N/A'

                        try:
                            date = result['observed_on_details']['date']
                        except KeyError as e:
                            print(f"KeyError in file {json_file_path}: {e}. Recording 'N/A' for 'Observation Date'.")

                        try:
                            iconic_taxon_name = result['taxon']['iconic_taxon_name']
                        except KeyError as e:
                            print(f"KeyError in file {json_file_path}: {e}. Recording 'N/A' for 'Iconic Taxon Name'.")

                        try:
                            preferred_common_name = result['taxon']['preferred_common_name'].title()#I think this should make all first letters uppercase 
                        except KeyError as e:
                            print(f"KeyError in file {json_file_path}: {e}. Recording 'N/A' for 'Preferred Common Name'.")

                        try:
                            longitude = result['geojson']['coordinates'][0]
                        except KeyError as e:
                            print(f"KeyError in file {json_file_path}: {e}. Recording 'N/A' for 'Longitude'.")

                        try:
                            latitude = result['geojson']['coordinates'][1]
                        except KeyError as e:
                            print(f"KeyError in file {json_file_path}: {e}. Recording 'N/A' for 'Latitude'.")

                        if iconic_taxon_name==taxon:

                            csv_writer.writerow([gardenname, date, iconic_taxon_name, preferred_common_name,latitude,longitude,])

            




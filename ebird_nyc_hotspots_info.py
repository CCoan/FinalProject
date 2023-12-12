#uses eBird API to get locations of hotspots in NYC

import requests
import json
import csv

extracted_data = []
all_headers = ["Name of Hotspot", "Latest Observation Date", "Total Species Observed", "Latitude", "Longitude"]

region_codes=["061","005","081","047","085"]#Region codes for the 5 NYC boroughts 

for region_code in region_codes:

    url = f"https://api.ebird.org/v2/ref/hotspot/US-NY-{region_code}"



    headers = {'Content-Type': 'application/json'}
    params = {
            "key": "gqrrpnl833pv", 
            "fmt":"json"
            }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        if data:
            for entry in data:
                hotspot_name = entry.get("locName", "N/A")
                latest_observation_date = entry.get("latestObsDt", "N/A")
                species_observed = entry.get("numSpeciesAllTime", "N/A")
                latitude = entry.get("lat", "N/A")
                longitude = entry.get("lng", "N/A")

                extracted_data.append({
                    "Name of Hotspot": hotspot_name,
                    "Latest Observation Date": latest_observation_date,
                    "Total Species Observed": species_observed,
                    "Latitude": latitude,
                    "Longitude": longitude
                })
#used Chat GPT for error handling
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        # Handle the error, log it, or take appropriate action

# Write extracted data to CSV file 
with open("res/ebird_hotspot_data.csv", 'w', newline='') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=all_headers)

    # Write headers to the CSV file
    csv_writer.writeheader()

    # Write data to the CSV file
    csv_writer.writerows(extracted_data)
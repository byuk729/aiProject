# uses permission to get real data

import requests     
import json
import csv

# removed 
ACCESS_TOKEN = "fake_access"

# Kroger Locations API endpoint
url = "https://api.kroger.com/v1/locations"

# Header for GET request
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

#Query parameters for filtering stores
params = {
    "filter.zipCode.near": "22903",
    "filter.radiusInMiles": 10,
    "filter.limit": 10
}

# Send GET request to Locations API
response = requests.get(url, headers=headers, params=params)

# Convert response into JSON
data = response.json()

#Extract the list of stores (API wraps it inside "data")
stores = data.get("data", [])

#Path to output CSV file
output_file ="../clean/stores.csv"

# Open file in write mode
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # Write the header row first
    writer.writerow([
        "store_id",
        "store_name",
        "address",
        "city",
        "state",
        "zip_code",
        "latitude",
        "longitude"
    ])

    #Loop through each store and extract relevant fields
    for store in stores:
        store_id = store.get("locationId")
        name = store.get("name")

        address_info = store.get("address", {})
        address = address_info.get("addressLine1")
        city = address_info.get("city")
        state = address_info.get("state")
        zip_code = address_info.get("zipCode")

        geo = store.get("geolocation", {})
        latitude = geo.get("latitude")
        longitude = geo.get("longitude")

        writer.writerow([
            store_id,
            name,
            address,
            city,
            state,
            zip_code,
            latitude,
            longitude
        ])

print(f"Saved {len(stores)} stores to {output_file}")
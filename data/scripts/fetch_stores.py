import requests     
import json

ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiWjRGZDNtc2tJSDg4aXJ0N0xCNWM2Zz09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJjaGFybG90dGVzdmlsbGVncm9jZXJpZXNmaW5kZXJwcm9qZWN0LWJiY2R4OXhwIiwiZXhwIjoxNzc0NjQ5NTE4LCJpYXQiOjE3NzQ2NDc3MTMsImlzcyI6ImFwaS5rcm9nZXIuY29tIiwic3ViIjoiNWQzM2QzZWItYWI5OC01NzYzLWEyNDQtNzhkMTI2NTdmNmM3Iiwic2NvcGUiOiIiLCJhdXRoQXQiOjE3NzQ2NDc3MTg1MzY5NjM0MjAsImF6cCI6ImNoYXJsb3R0ZXN2aWxsZWdyb2Nlcmllc2ZpbmRlcnByb2plY3QtYmJjZHg5eHAifQ.AYVUYtvJadJEqCFzkBVNta1EksWf8iVRc_S8ZRx5JAIF_msE9Yn9F_E23oS3ZOeYuHPVELMPPKz2JPBbqRIRZdmDHPS7rWUJKNAH2OksfrcRYtdZGWNQLXAIVorR0xd8OoBw_CO6djm_Ucr97Hb1uYsR1f70i7jaLAhq0Fpq-vWG7rt0YM3_HKdr9W7mWCvipI_7L8mOLMMtscJQtrjTcqaax-IEFWLVZ7ZB9tpdE-k9B4tEQ9BHmuluOyjwr1BcizCw4I6CTX2NZwwRDpkYfp6DD7u-eZAQvdpbbNiLkcK4HhzSXycBuUHUDHIYmw4iUfJ6Juvv4nleom3iEpd6BA"

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

    print([
        store_id,
        name,
        address,
        city,
        state,
        zip_code,
        latitude,
        longitude
    ])
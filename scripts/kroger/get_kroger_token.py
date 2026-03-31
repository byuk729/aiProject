# gets permission (token)

import requests
import base64

# App credentials from Kroger developer portal (removed for now)
CLIENT_ID = "charlottesvillegroceriesfinderproject-bbcdx9xp"
CLIENT_SECRET = "w4mPctUGuDcm4rkiXm9JQVk39ngFONEI6N1jPoZX"

def get_access_token(scope):
    # Kroger token endpoint
    url = "https://api.kroger.com/v1/connect/oauth2/token"

    # Combine into one string and encode client_id:client_secret in base64
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    # Headers for the POST request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }

    # Body of the request; grant_type tells Kroger which OAuth flow we are using 
    data = {
        "grant_type": "client_credentials",
        "scope": scope
    }

    # Send POST request to get access token
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

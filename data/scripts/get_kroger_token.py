import requests
import base64

# App credentials from Kroger developer portal
CLIENT_ID = "charlottesvillegroceriesfinderproject-bbcdx9xp"
CLIENT_SECRET = "FQTNv5vcKXH8NVye9qNInHoh29B5MHF6YikApMRA"

# Kroger token endpoint
url = "https://api.kroger.com/v1/connect/oauth2/token"

# Combine into one string and encode client_id:client_secret in base64
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Headers for the POST request
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {encoded_credentials}",
}

# Body of the request; grant_type tells Kroger which OAuth flow we are using 
data = {
    "grant_type": "client_credentials"
}

# Send POST request to get access token
response = requests.post(url, headers=headers, data=data)

# Print status and token for debugging
print("Status code:", response.status_code)
print("Response:")
print(response.text)
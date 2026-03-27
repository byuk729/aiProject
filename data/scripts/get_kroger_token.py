import requests
import base64

CLIENT_ID = "charlottesvillegroceriesfinderproject-bbcdx9xp"
CLIENT_SECRET = "FQTNv5vcKXH8NVye9qNInHoh29B5MHF6YikApMRA"

# Kroger token endpoint
url = "https://api.kroger.com/v1/connect/oauth2/token"

# Encode client_id:client_secret in base64
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {encoded_credentials}",
}

data = {
    "grant_type": "client_credentials"
}

response = requests.post(url, headers=headers, data=data)

print("Status code:", response.status_code)
print("Response:")
print(response.text)
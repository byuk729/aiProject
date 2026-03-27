import requests
import json

ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiWjRGZDNtc2tJSDg4aXJ0N0xCNWM2Zz09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJjaGFybG90dGVzdmlsbGVncm9jZXJpZXNmaW5kZXJwcm9qZWN0LWJiY2R4OXhwIiwiZXhwIjoxNzc0NjQ5NTE4LCJpYXQiOjE3NzQ2NDc3MTMsImlzcyI6ImFwaS5rcm9nZXIuY29tIiwic3ViIjoiNWQzM2QzZWItYWI5OC01NzYzLWEyNDQtNzhkMTI2NTdmNmM3Iiwic2NvcGUiOiIiLCJhdXRoQXQiOjE3NzQ2NDc3MTg1MzY5NjM0MjAsImF6cCI6ImNoYXJsb3R0ZXN2aWxsZWdyb2Nlcmllc2ZpbmRlcnByb2plY3QtYmJjZHg5eHAifQ.AYVUYtvJadJEqCFzkBVNta1EksWf8iVRc_S8ZRx5JAIF_msE9Yn9F_E23oS3ZOeYuHPVELMPPKz2JPBbqRIRZdmDHPS7rWUJKNAH2OksfrcRYtdZGWNQLXAIVorR0xd8OoBw_CO6djm_Ucr97Hb1uYsR1f70i7jaLAhq0Fpq-vWG7rt0YM3_HKdr9W7mWCvipI_7L8mOLMMtscJQtrjTcqaax-IEFWLVZ7ZB9tpdE-k9B4tEQ9BHmuluOyjwr1BcizCw4I6CTX2NZwwRDpkYfp6DD7u-eZAQvdpbbNiLkcK4HhzSXycBuUHUDHIYmw4iUfJ6Juvv4nleom3iEpd6BA"

url = "https://api.kroger.com/v1/locations"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

params = {
    "filter.zipCode.near": "22903",
    "filter.radiusInMiles": 10,
    "filter.limit": 10
}

response = requests.get(url, headers=headers, params=params)

print("Status code:", response.status_code)

data = response.json()
print(json.dumps(data, indent=2))
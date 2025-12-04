import requests
import json

API_KEY = "901124e8-7fca-4468-85a8-075ef29dd819"
DEVICE_ID = "69312c2dd3fdd9bd6c54dfc7"

url = f"https://api.textbee.dev/api/v1/gateway/devices/{DEVICE_ID}/get-received-sms"
headers = {"x-api-key": API_KEY}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        messages = data.get('data', [])
        if messages:
            print("First message keys:", messages[0].keys())
            print("First message sample:", json.dumps(messages[0], indent=2))
        else:
            print("No messages found.")
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Exception: {e}")

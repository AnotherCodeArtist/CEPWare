import requests

url = 'http://localhost:1026/v2/subscriptions/'

headers = {'Content-Type': 'application/json',
			'fiware-service': 'cepware',
			'fiware-servicepath': '/rooms'}

payload = {
    "description": "A subscription to get info about the tempearture of the rooms",
    "subject": {
        "entities": [
            {
                "idPattern": ".*"
            }
        ]
    },
    "notification": {
        "http": {
            "url": "http://taskmanager:9001/notify"
        },
        "attrs": [
            "temperature"
        ]
    },
    "throttling": 5
}

r = requests.post(url, headers = headers, json = payload)
statusCode = r.status_code
print(statusCode)
if (statusCode > 399 | statusCode < 599):
  print(r.raise_for_status())

import requests

url = 'http://localhost:1026/v2/entities'

headers = {'Content-Type': 'application/json',
			'fiware-service': 'cepware',
			'fiware-servicepath': '/rooms'}

payload = {
    "id": "R4",
    "type": "Room",
    "temperature": {
        "type": "Float",
        "value": 23.1
    }
}

r = requests.post(url, headers = headers, json = payload)
statusCode = r.status_code
print(statusCode)
if (statusCode > 399 | statusCode < 599):
  print(r.raise_for_status())

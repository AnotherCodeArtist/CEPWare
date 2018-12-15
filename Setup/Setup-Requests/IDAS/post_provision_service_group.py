import requests

url = 'http://localhost:4041/iot/services'

headers = {'Content-Type': 'application/json',
			'fiware-service': 'cepware',
			'fiware-servicepath': '/rooms',
           'X-Auth-Token': 'a-token'}

payload = {
    "services": [
        {
            "apikey": "test",
            "cbroker": "http://orion:1026",
            "entity_type": "Room",
            "resource": "/iot/d"
        }
    ]
}

r = requests.post(url, headers = headers, json = payload)
statusCode = r.status_code
print(statusCode)
if (statusCode > 399 | statusCode < 599):
  print(r.raise_for_status())

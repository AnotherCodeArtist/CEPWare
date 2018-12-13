import requests

url = 'http://localhost:4041/iot/devices'

headers = {'Content-Type': 'application/json',
			'fiware-service': 'cepware',
			'fiware-servicepath': '/rooms',
           'X-Auth-Token': 'a-token'}

payload = {
    "devices": [
        {
            "device_id": "IoT-R4",
            "entity_name": "R4",
            "entity_type": "Room",
            "timezone": "Europe/Madrid",
            "attributes": [
                {
                    "object_id": "t",
                    "name": "temperature",
                    "type": "float"
                }
            ],
            "static_attributes": [
                {
                    "name": "att_name",
                    "type": "string",
                    "value": "value"
                }
            ]
        }
    ]
}

r = requests.post(url, headers = headers, json = payload)
statusCode = r.status_code
print(statusCode)
if (statusCode > 399 | statusCode < 599):
  print(r.raise_for_status())

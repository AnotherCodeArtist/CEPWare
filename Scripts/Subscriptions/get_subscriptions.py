import requests
import json

url = 'http://localhost:1026/v2/subscriptions/'

headers = {
			'fiware-service': 'cepware',
			'fiware-servicepath': '/rooms'
}

r = requests.get(url, headers = headers)
print(r.text)
import counter
import time
import random
import requests

payload = ""

count = counter.Counter()
count.start()

if count.peek() <= 20:
    payload = "t|20"
elif count.peek() <= 50:
    payload = "t|" + str(count.peek())
else:
    payload = "t|" + str(random.randint(30, 90))

url = "http://localhost:7896/iot/d?k=test&i=IoT-R" + str(random.randint(0, 5))
headers = {"Fiware-Service": "cepware", "Fiware-ServicePath": "/rooms", "Content-Type": "text/plain"}

r = requests.post(url, headers=headers, data=payload)

time.sleep(5)
print(payload)

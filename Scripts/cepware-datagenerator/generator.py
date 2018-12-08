import random

import requests

import counter


class Generator:
    def __init__(self):
        self.payload = ""
        self.url = ""
        self.headers = {}
        self.count = counter.Counter()

    def main(self):
        self.count.start()

        while self.count.peek() <= 20:
            self.payload = "t|20"
            print(self.payload)
        while self.count.peek() <= 50:
            self.payload = "t|" + str(self.count.peek())
            print(self.payload)
        while self.count.peek() <= 120:
            self.payload = "t|" + str(random.randint(30, 90))
            print(self.payload)

        # self.url = "http://localhost:7896/iot/d?k=test&i=IoT-R" + str(random.randint(0, 5))
        self.url = "https://httpbin.org/post"
        self.headers = {"Fiware-Service": "cepware", "Fiware-ServicePath": "/rooms", "Content-Type": "text/plain"}

        requests.post(self.url, headers=self.headers, data=self.payload)


g = Generator()
g.main()

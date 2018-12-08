import random
import sys

import requests

import counter


class Generator:
    def __init__(self):
        self.payload = ""
        self.url = ""
        self.headers = {}
        self.count = counter.Counter()
        if sys.argv[1] == "--strategy":
            self.mode = sys.argv[2]
        else:
            self.mode = "normal"

    def main(self):
        self.generate(self.mode)

    def generate(self, strategy):
        self.count.start()
        while True:
            if strategy == "normal":
                self.payload = "t|20"
                self.send_out(self.payload)
                print(self.payload)
            elif strategy == "fire":
                self.payload = "t|" + str(self.count.peek() + 20)
                self.send_out(self.payload)
                print(self.payload)
            elif strategy == "failure":
                self.payload = "t|" + str(random.randint(30, 90))
                self.send_out(self.payload)
                print(self.payload)

    def send_out(self, payload):
        # self.url = "http://localhost:7896/iot/d?k=test&i=IoT-R" + str(random.randint(0, 5))
        self.url = "https://httpbin.org/post"
        self.headers = {"Fiware-Service": "cepware", "Fiware-ServicePath": "/rooms", "Content-Type": "text/plain"}

        requests.post(self.url, headers=self.headers, data=payload)


g = Generator()
g.main()

#!/usr/bin/python
import sys
import requests
import time
import ast

print(
    "Enter a simulation strategy. You can simulate fire, failure, minimum and maximum case and test")
possibleStrategies = ["fire", "minmax", "failure"]
inputStrategy = input(
    "Please enter the strategy. For Fire 'fire', Failure 'failure' and minmax 'minmax'\n")
if inputStrategy in possibleStrategies:
    correct = True
    strategy = inputStrategy
else:
    correct = False
while correct == False:
    inputStrategy = input(
        str(inputStrategy) + " is not a valid strategy. Please enter: 'fire', 'failure', 'normal' or 'test'.\n")
    if inputStrategy in possibleStrategies:
        correct = True
        strategy = inputStrategy
    else:
        correct = False

urls = ["http://localhost:7896/iot/d?k=test&i=IoT-R1", "http://localhost:7896/iot/d?k=test&i=IoT-R2",
        "http://localhost:7896/iot/d?k=test&i=IoT-R3", "http://localhost:7896/iot/d?k=test&i=IoT-R4",
        "http://localhost:7896/iot/d?k=test&i=IoT-R5"]


def generateData(urlList, strategyType):
    if strategyType == "fire":
        for tmp in range(25, 100, 5):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)

    elif strategyType == "minmax":
        for tmp in range(60, 75):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)
        for tmp in reversed(range(0, 15)):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)

    elif strategyType == "failure":
        for tmp in range(20, 23):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)
        urlWithOutR5 = urlList[0:4]
        for tmp in range(24, 40):
            payload = "t|" + str(tmp)
            for url in urlWithOutR5:
                makeRequest(url, payload)

    else:
        print("Something went wrong! Your input: " + strategy)


def makeRequest(url, payload):
    headers = {'Content-Type': 'text/plain',
               'fiware-service': 'cepware',
               'fiware-servicepath': '/rooms'}
    try:
        r = requests.post(url, headers=headers, data=payload)
        statusCode = r.status_code
        r.raise_for_status()
        print("Sent " + payload + " to URL: " + url + ". Statuscode: " + str(statusCode))
        time.sleep(.300)
    except (ConnectionError, ConnectionRefusedError, requests.exceptions.HTTPError):
        if (statusCode > 399):
            print("Connection refused. Statuscode is: " + str(
                statusCode) + ". Bad request! Check if infrastructure is set up.")
        else:
            print(
                "Something went wrong while sending the request to URL: " + url + " ;with payload: " + payload + ". Statuscode: " + str(
                    statusCode))
        time.sleep(.300)


generateData(urls, strategy)

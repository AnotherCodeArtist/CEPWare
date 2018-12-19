#!/usr/bin/python
import sys
import requests
import time
import ast


urls = ["http://localhost:7896/iot/d?k=test&i=IoT-R1", "http://localhost:7896/iot/d?k=test&i=IoT-R2",
        "http://localhost:7896/iot/d?k=test&i=IoT-R3", "http://localhost:7896/iot/d?k=test&i=IoT-R4",
        "http://localhost:7896/iot/d?k=test&i=IoT-R5"]
strategy = ""
try:
    args = str(sys.argv)
    strategy = ast.literal_eval(args)[2]
except (IndexError):
    print("Script started as standalone. Please follow the instructions.")

print(
    "Enter a strategy. For simulating fire enter 'fire', for a failure enter 'failure', for a test case enter 'test', and for a normal case enter 'normal'")
possibleStrategies = ["fire", "minmax", "failure", "test"]
inputStrategy = input("Please enter the strategy.\n")
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
print("Do you want to send the requests to local or the server?")

anotherURL = input("For server enter 'y' for local enter 'n'\n")
if anotherURL == "y":
    urls = ["http://10.25.2.146:7896/iot/d?k=test&i=IoT-R1", "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R2",
            "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R3", "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R4",
            "http://10.25.2.146:7896/iot/d?k=test&i=IoT-R5"]



def generateData(urlList, strategyType):
    if strategyType == "fire":
        for tmp in range(25, 75):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)
        ''' Optional:
        payload = "t|70"
        cond = True
        while cond:
            for url in urlList:
                makeRequest(url, payload)
                '''

    elif strategyType == "minmax":
        for tmp in range(60, 80):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)
        for tmp in range(15, 0):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)
        ''' Optional:
        payload = "t|0"
        cond = True
        while cond:
            for url in urls:
                makeRequest(url, payload)
                '''

    elif strategyType == "failure":
        for tmp in range(20, 23):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)
        urlWithOutR5 = urlList.remove(4)
        for tmp in range(24, 40):
            payload = "t|" + str(tmp)
            for url in urlWithOutR5:
                makeRequest(url, payload)

        '''Optional:
        cond = True
        while cond:
            for url in urlWithOutR5:
                makeRequest(url, payload)
                '''

    elif strategyType == "test":
        for tmp in range(20, 25):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)

    else:
        print("Something went wrong! Your input: " + strategy)


def makeRequest(url, payload):
    headers = {'Content-Type': 'text/plain',
               'fiware-service': 'cepware',
               'fiware-servicepath': '/rooms'}
    try:
        print (url, headers, payload)
        r = requests.post(url, headers=headers, data=payload)
        statusCode = r.status_code
        r.raise_for_status()
        print("Sent " + payload + "to URL: " + url + ". Statuscode: " + str(statusCode))
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

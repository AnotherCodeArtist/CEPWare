#!/usr/bin/python
import sys
import requests
import time

args = str(sys.argv)
if input != None:
    print(
        "Please enter the strategy. For simulating fire enter 'fire', for a failure enter 'failure', for a test case enter 'test', and for a normal case enter 'normal'")
    input_var = input("Please enter the strategy.\n")
    strategy = input_var
else:
    strategy = args[1]

urls = ["http://localhost:7896/iot/d?k=test&i=IoT-R1", "http://localhost:7896/iot/d?k=test&i=IoT-R2",
        "http://localhost:7896/iot/d?k=test&i=IoT-R3", "http://localhost:7896/iot/d?k=test&i=IoT-R4",
        "http://localhost:7896/iot/d?k=test&i=IoT-R5"]


def generateData(urlList, strategyType):
    if strategyType == "normal":
        payload = "t|20"
        cond = True
        while cond:
            for url in urlList:
                makeRequest(url, payload)

    elif strategyType == "fire":
        tmp = 20
        for tmp in range(20, 50):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)
        payload = "t|50"
        cond = True
        while cond:
            for url in urlList:
                makeRequest(url, payload)

    elif strategyType == "failure":
        for tmp in range(20, 100):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)
        payload = "t|100"
        cond = True
        while cond:
            for url in urls:
                makeRequest(url, payload)

    elif strategyType == "test":
        for tmp in range(20, 35):
            payload = "t|" + str(tmp)
            for url in urlList:
                makeRequest(url, payload)

    else:
        print("Something went wrong! Your input: " + strategy)


def makeRequest(url, payload):
    headers = {'Content-Type': 'application/json',
               'fiware-service': 'cepware',
               'fiware-servicepath': '/rooms'}
    try:
        r = requests.post(url, headers=headers, data=payload)
        statusCode = r.status_code
        r.raise_for_status()
        print("Sent " + payload + "to URL: " + url + ". Statuscode: " + str(statusCode))
        time.sleep(.300)
    except (ConnectionError, ConnectionRefusedError, requests.exceptions.HTTPError):
        if (statusCode > 399):
            print("Connection refused. Statuscode is: " + str(statusCode) + ". Bad request! Check if infrastructure is set up." )
        else:
            print(
                "Something went wrong while sending the request to URL: " + url + " ;with payload: " + payload + ". Statuscode: " + str(
                    statusCode))
        time.sleep(.300)


generateData(urls, strategy)

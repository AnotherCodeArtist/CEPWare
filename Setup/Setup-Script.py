#!/usr/bin/python
# This is a Python 3 File

import os
import subprocess
import tarfile
import requests
import time
import docker
import json


#### Welcome
print(
    "Welcome to CEPWARE. This is the automated setup. Before you run this script. Please do a docker-compose up. "
    "Please follow the instructions and be patient until everything is setup")

#### Check if the given Path is correct
inputPath = input(
    "Please Enter the Full Path to your CEPWARE folder. \n Under Windows it could e.g. be C:\\Workspace\\CEPWARE, "
    "here we need C:\\Workspace)\n")
checkSource = os.path.join(inputPath, "CEPWARE", "cepware", "target")
try:
    os.chdir(checkSource)
    validPath = True
except FileNotFoundError:
    print("FILE or PATH NOT FOUND! CHECK YOUR PATH TO THE CEPware FOLDER")
    validPath = False
while validPath == False:
    inputPath = input("Your path: " + inputPath + " was not correct. Please reenter the correct path!\n")
    checkSource = os.path.join(inputPath, "CEPWARE", "cepware", "target")
    try:
        os.chdir(checkSource)
        validPath = True
    except FileNotFoundError:
        print("FILE or PATH NOT FOUND! CHECK YOUR PATH TO THE CEPware FOLDER")
        validPath = False


#### Staring the data script ?
print("Do you also want to start the automated data script ?\n")
dataGeneration = input("For yes enter 'y' otherwise 'n'.\n")
possibleStrategies = ["fire", "normal", "failure", "test"]
if (dataGeneration == "y"):
    inputStrategy = input(
        "Please enter the strategy you want to simulate later. ('fire', 'failure', 'normal', 'test').\n")
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

#### Setting paths to the components and getting the container id of the jobmanager
client = docker.from_env()
container = client.containers.get("jobmanager")
containerId = container.id
source = os.path.join(inputPath, "CEPware", "cepware", "target", "cepware-1.5.jar")
destination = (containerId + ":" + "/opt/flink/cepware-1.5.jar")


##### Function to copy the Apache Flink Jar to the Taskmanager (Docker Apache FLink Container)
# First we generate a tar file of the jar file which we copy into the container
def copy_to(src, dst):
    name, dst = dst.split(':')

    os.chdir(os.path.dirname(src))
    srcname = os.path.basename(src)

    tar = tarfile.open(src + '.tar', mode='w')
    try:
        tar.add(srcname)
    finally:
        tar.close()

    data = open(src + '.tar', 'rb').read()
    container.put_archive(os.path.dirname(dst), data)


#### Copy tar file to container and execute it.
print("Starting Apache Flink. Please be patient...")
copy_to(source, destination)
container.exec_run(cmd="flink run -d ./cepware-1.5.jar", workdir="/opt/flink/")
print("Apache Flink is up and running.")


print("Sending requests to set up the infrastructure-")
#### Function to make Requests
def makeRequest(inputUrl, inputHeaders, inputPayload):
    try:
        r = requests.post(inputUrl, headers=inputHeaders ,json=inputPayload)
        statusCode = r.status_code
        r.raise_for_status()
        if statusCode == 200 or statusCode == 201:
            print("Request to URL: " + inputUrl + " was succesful with statuscode: " + str(statusCode))
        else:
            print("Sent Request to URL: " + inputUrl + ". Statuscode: " + str(statusCode))
    except (ConnectionError, ConnectionRefusedError, requests.exceptions.HTTPError):
        if (statusCode == 400):
            print("Bad request! Statuscode is: " + str(
                statusCode) + ". Check if infrastructure is already set up.")
        elif statusCode == 409 or statusCode == 422:
            print("Device is already registered! Statuscode: " + str(statusCode))
        else:
            print(
                "Something went wrong while sending the request to URL: " + inputUrl +  ". Statuscode: " + str(
                    statusCode))


#### Define Request URLS, HEADERS and PAYLOADS
urlOrionSubscription = 'http://localhost:1026/v2/subscriptions/'
urlOrionEntities = 'http://localhost:1026/v2/entities'
urlIdasEntities = 'http://localhost:4041/iot/devices'
urlIdasServices = 'http://localhost:4041/iot/services'

normalHeaders = {'Content-Type': 'application/json',
                 'fiware-service': 'cepware',
                 'fiware-servicepath': '/rooms'}

headersIdas = {'Content-Type': 'application/json',
               'fiware-service': 'cepware',
               'fiware-servicepath': '/rooms',
               'X-Auth-Token': 'a-token'}


def makePayloadSubscriptions(component, port):
    payload = {
        "description": "Subscription for component: " + component,
        "subject": {
            "entities": [
                {
                    "idPattern": ".*"
                }
            ]
        },
        "notification": {
            "http": {
                "url": "http://" + component + ":" + str(port) + "/notify"
            },
            "attrs": [
                "temperature"
            ]
        },
        "throttling": 5
    }
    return payload


def makePayloadOrionEntities(entity):
    payload = {
        "id": entity,
        "type": "Room",
        "temperature": {
            "type": "Float",
            "value": 22
        }
    }
    return payload


payloadIdasRegisterServiceGroup = {
    "services": [
        {
            "apikey": "test",
            "cbroker": "http://orion:1026",
            "entity_type": "Room",
            "resource": "/iot/d"
        }
    ]
}


def makePayLoadIdasEntities(iot, ent):
    payload = {
        "devices": [
            {
                "device_id": iot,
                "entity_name": ent,
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
    return payload


requestDict = {"post_subscription_cygnus": (1, "cygnus", 5050),
               "post_subscription_flink": (1, "flink", 9001),
               "post_create_R1": (2, "R1"), "post_create_R2": (2, "R2"),
               "post_create_R3": (2, "R3"), "post_create_R4": (2, "R4"),
               "post_create_R5": (2, "R5"), "post_provision_service_group": (3, "fill"),
               "post_register_IoT-R1": (4, "IoT-R1", "R1"),
               "post_register_IoT-R2": (4, "IoT-R2", "R2"), "post_register_IoT-R3": (4, "IoT-R3", "R3"),
               "post_register_IoT-R4": (4, "IoT-R4", "R4"), "post_register_IoT-R5": (4, "IoT-R5", "R5")}

for k, v in requestDict.items():
    if v[0] == 1:
        makeRequest(urlOrionSubscription, normalHeaders, makePayloadSubscriptions(v[1], v[2]))
    elif v[0] == 2:
        makeRequest(urlOrionEntities, normalHeaders, makePayloadOrionEntities(v[1]))
    elif v[0] == 3:
        #print(urlIdasServices, headersIdas, payloadIdasRegisterServiceGroup)
        makeRequest(urlIdasServices, headersIdas, payloadIdasRegisterServiceGroup)
    else:
        #print(makePayLoadIdasEntities(v[1], v[2]))
        makeRequest(urlIdasEntities, headersIdas, makePayLoadIdasEntities(v[1], v[2]))
print("The infrastructure is up and running.")

if dataGeneration == "y":
    print("Starting Data Generation now! Exit with ctrl-c!")
    subprocess.call(
        ["python", (os.path.join(inputPath, "CEPware", "Setup", "data-generator.py -strategy=" + strategy))])
    print("The whole system is up and running. You will now see the Data begin sent.")
else:
    print("The system is set up and the automated Data script has not been started.")
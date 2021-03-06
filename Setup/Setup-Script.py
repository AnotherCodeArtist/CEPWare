#!/usr/bin/python
# This is a Python 3 File

import os
import platform
import subprocess
import sys
import tarfile

import docker
import requests

#### Welcome
print(
    "Welcome to CEPWARE. This is the automated setup. Before you run this script. Please do a docker-compose up. "
    "Please follow the instructions and be patient until everything is setup")

#### Check if the given Path is correct
inputPath = input(
    "Please Enter the Full Path to your CEPWARE folder. \n Under Windows it could e.g. be C:\\Workspace\\CEPWare, "
    "here we need C:\\Workspace)\n")
checkSource = os.path.join(inputPath, "CEPWare", "Application")
try:
    os.chdir(checkSource)
    validPath = True
except FileNotFoundError:
    print("FILE or PATH NOT FOUND! CHECK YOUR PATH TO THE CEPWare FOLDER")
    validPath = False
while validPath == False:
    inputPath = input("Your path: " + inputPath + " was not correct. Please reenter the correct path!\n")
    checkSource = os.path.join(inputPath, "CEPWare", "Application")
    try:
        os.chdir(checkSource)
        validPath = True
    except FileNotFoundError:
        print("FILE or PATH NOT FOUND! CHECK YOUR PATH TO THE CEPWare FOLDER")
        validPath = False

#### Staring the data script ?
print("Do you also want to start the automated data script ?\n")
dataGeneration = input("For yes enter 'y' otherwise 'n'.\n")

#### Setting paths to the components and getting the container id of the jobmanager
try:
    client = docker.from_env()
    jobmanager = client.containers.get("jobmanager")
    jobmanagerId = jobmanager.id
    taskmanager = client.containers.get("taskmanager")
    taskmanagerId = taskmanager.id
except docker.errors.NotFound:
    print("Docker is not started or docker-compose up has not been run. Check if Docker is up and running")
    sys.exit(1)
sourceTaskManagerConfig = os.path.join(inputPath, "CEPWare", "Setup", "flink-conf.yaml")
sourceMinMax = os.path.join(inputPath, "CEPWare", "Application", "cep-min-max-1.6.jar")
sourceFire = os.path.join(inputPath, "CEPWare", "Application", "cep-temp-rise-1.6.jar")
sourceFailure = os.path.join(inputPath, "CEPWare", "Application", "cep-timeout-1.6.jar")
destinationMinMax = (jobmanagerId + ":" + "/opt/flink/cep-min-max-1.6.jar")
destinationFire = (jobmanagerId + ":" + "/opt/flink/cep-temp-rise-1.6.jar")
destinationFailure = (jobmanagerId + ":" + "/opt/flink/cep-timeout-1.6.jar")
destinationTaskManagerConfig = (taskmanagerId + ":" + "/opt/flink/conf/flink-conf.yaml")


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
    if name == jobmanagerId:
        jobmanager.put_archive(os.path.dirname(dst), data)
    else:
        taskmanager.put_archive(os.path.dirname(dst), data)


#### Copy tar file to container and execute it.
print("Starting Apache Flink. Please be patient...")

copy_to(sourceMinMax, destinationMinMax)
copy_to(sourceFire, destinationFire)
copy_to(sourceFailure, destinationFailure)

print("Apache Flink is up and running.")

print("Sending requests to set up the infrastructure")


#### Function to make Requests
def makeRequest(inputUrl, inputHeaders, inputPayload):
    try:
        r = requests.post(inputUrl, headers=inputHeaders, json=inputPayload)
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
                "Something went wrong while sending the request to URL: " + inputUrl + ". Statuscode: " + str(
                    statusCode))


#### Define Request URLS, HEADERS and PAYLOADS
urlOrionSubscription = 'http://localhost:1026/v2/subscriptions/'
urlOrionEntities = 'http://localhost:1026/v2/entities'
urlIdasEntities = 'http://localhost:4041/iot/devices'
urlIdasServices = 'http://localhost:4041/iot/services'

normalHeaders = {'Content-Type': 'application/json',
                 'Fiware-service': 'cepware',
                 'Fiware-servicepath': '/rooms'}

headersIdas = {'Content-Type': 'application/json',
               'Fiware-service': 'cepware',
               'Fiware-servicepath': '/rooms',
               'X-Auth-Token': 'a-token'}


def makePayloadSubscriptions(component, port):
    payload = {
        "description": "Subscription for component: " + component,
        "subject": {
            "entities": [
                {
                    "idPattern": ".*"
                }
            ],
        },
        "notification": {
            "http": {
                "url": "http://" + component + ":" + str(port) + "/notify"
            },
            "attr": [
                "temperature"
            ]
        },
    }
    return payload


cygnusSubscription = {
    "description": "Subscription for component: Cygnus",
    "subject": {
        "entities": [
            {
                "idPattern": ".*"
            }
        ],
    },
    "notification": {
        "http": {
            "url": "http://cygnus:5050/notify"
        },
        "attrsFormat": "legacy"
    }
}


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
                "timezone": "Europe/Vienna",
                "attributes": [
                    {
                        "object_id": "t",
                        "name": "temperature",
                        "type": "float"
                    }
                ]
            }
        ]
    }
    return payload


requestDict = {"post_subscription_cygnus": (0, "fill"),
               "post_subscription_flink1": (1, "taskmanager", 9002),
               "post_subscription_flink2": (1, "taskmanager", 9003),
               "post_subscription_flink3": (1, "taskmanager", 9004),
               "post_create_R1": (2, "R1"), "post_create_R2": (2, "R2"),
               "post_create_R3": (2, "R3"), "post_create_R4": (2, "R4"),
               "post_create_R5": (2, "R5"), "post_provision_service_group": (3, "fill"),
               "post_register_IoT-R1": (4, "IoT-R1", "R1"),
               "post_register_IoT-R2": (4, "IoT-R2", "R2"), "post_register_IoT-R3": (4, "IoT-R3", "R3"),
               "post_register_IoT-R4": (4, "IoT-R4", "R4"), "post_register_IoT-R5": (4, "IoT-R5", "R5")}

for k, v in requestDict.items():
    if v[0] == 0:
        makeRequest(urlOrionSubscription, normalHeaders, cygnusSubscription)
    elif v[0] == 1:
        makeRequest(urlOrionSubscription, normalHeaders, makePayloadSubscriptions(v[1], v[2]))
    elif v[0] == 2:
        makeRequest(urlOrionEntities, normalHeaders, makePayloadOrionEntities(v[1]))
    elif v[0] == 3:
        makeRequest(urlIdasServices, headersIdas, payloadIdasRegisterServiceGroup)
    else:
        makeRequest(urlIdasEntities, headersIdas, makePayLoadIdasEntities(v[1], v[2]))

jobmanager.exec_run(cmd="flink run -d ./cep-min-max-1.6.jar", workdir="/opt/flink/")
jobmanager.exec_run(cmd="flink run -d ./cep-temp-rise-1.6.jar", workdir="/opt/flink/")
jobmanager.exec_run(cmd="flink run -d ./cep-timeout-1.6.jar", workdir="/opt/flink/")

print("The infrastructure is up and running.")
print("Deleting temporary files and cleaning up...")
try:
    os.remove(os.path.join(inputPath, "CEPWare", "Application", "cep-min-max-1.6.jar.tar"))
    os.remove(os.path.join(inputPath, "CEPWare", "Application", "cep-temp-rise-1.6.jar.tar"))
    os.remove(os.path.join(inputPath, "CEPWare", "Application", "cep-timeout-1.6.jar.tar"))
except FileNotFoundError:
    print("File not found! Aborting Clean-up and continuining with setup...")

if dataGeneration == "y":
    print("Starting Data Generation now! Exit with ctrl-c!")
    pathToDataGenerator = os.path.join(inputPath, "CEPWare", "Setup", "Data-Generator.py")
    os = platform.system()
    if os == "Windows":
        subprocess.run(
            ["python", pathToDataGenerator])
    else:
        subprocess.run(
            ["python3", pathToDataGenerator])
    print("The whole system is up and running. You will now see the Data begin sent.")
else:
    print("The system is set up and the automated Data script has not been started.")

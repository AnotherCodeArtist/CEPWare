#!/usr/bin/python

import os
import platform
import subprocess
import tarfile

import docker

# Get the OS platform
pltfrm = platform.system()
print(
    "Welcome to CEPWARE. This is the automated setup. Before you run this script. Please do a docker-compose up. "
    "Please follow the instructions and be patient until everything is setup")

input_var = input(
    "Please Enter the Full Path to your CEPWARE folder. \n Under Windows it could e.g. be C:\\Workspace\\CEPWARE, "
    "here we need C:\\Workspace)\n")
print("Do you also want to start the automated data script ?")
dataGeneration = input("For yes enter 'y' otherwise 'n'.")
if(dataGeneration == "y"):
    strategy = input("Please enter the strategy you want to simulate later. (fire, failure, normal)\n.")
    location = input("Please specify where the data should be sent to. (local, fh, test)\n")

# Based on the OS we have different seperators
if pltfrm == "Windows":
    # input_var = input_var.split(os.sep)
    slash = os.sep
else:
    # input_var = input_var.split(os.altsep)
    slash = os.altsep

source = os.path.join(input_var, "CEPware", "cepware", "target", "cepware-1.5.jar")

# Get the container id of the jobmanager
client = docker.from_env()
container = client.containers.get("jobmanager")
containerId = container.id
destination = (containerId + ":" + "/opt/flink/cepware-1.5.jar")


# Function to copy the Apache Flink Jar to the Taskmanager (Docker Apache FLink Container)
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


print("Starting Apache Flink. Please be patient...")
copy_to(source, destination)
# Execute the apache flink jar on the taskmanager
container.exec_run(cmd="flink run -d ./cepware-1.5.jar", workdir="/opt/flink/")
print("Apache Flink is up and running.")

print("Setting up the infrastructure and sending requests. Please be patient...")
# Call the requests
# Setup the Subscription from ORION to Cygnus

requests = [os.path.join("Subscriptions", "post_subscription_cygnus.py"),
            os.path.join("Subscriptions", "post_subscription_flink.py"),
            os.path.join("ORION", "post_create_R1.py"), os.path.join("ORION", "post_create_R2.py"),
            os.path.join("ORION", "post_create_R3.py"), os.path.join("ORION", "post_create_R4.py"),
            os.path.join("ORION", "post_create_R5.py"), os.path.join("IDAS", "post_provision_service_group.py"),
            os.path.join("IDAS", "post_register_IoT-R1.py"),
            os.path.join("IDAS", "post_register_IoT-R2.py"), os.path.join("IDAS", "post_register_IoT-R3.py"),
            os.path.join("IDAS", "post_register_IoT-R4.py"), os.path.join("IDAS", "post_register_IoT-R5.py")]

for req in requests:
    subprocess.call(["python", (
         os.path.join(input_var, "CEPware", "Setup", "Setup-Requests", req))])

print("The infrastructure is up and running.")

if dataGeneration == "y":
    print("Starting Datageneration now! Exit with ctrl-c!")
    generator_path = os.path.join(input_var, "CEPware", "Setup", "data-generator", "")

    if pltfrm == "Windows":
        subprocess.run([generator_path + "cepware-datagenerator-go.exe", "-strategy=" + strategy,
                        "-location=" + location])
    elif pltfrm == "Darwin":
        subprocess.run([generator_path + "cepware-datagenerator-go-darwin", "-strategy=" + strategy,
                        "-location=" + location])
    else:
        subprocess.run([generator_path + "cepware-datagenerator-go-linux", "-strategy=" + strategy,
                        "-location=" + location])

    print("The whole system is up and running. You will now see the Data begin sent.")
else:
    print("The system is set up and the automated Data script has not been started.")

#!/usr/bin/python

import os
import platform
import subprocess
import tarfile

import docker

pltfrm = platform.system()
print(
    "Welcome to CEPWARE. This is the automated setup. Before you run this script. Please do a docker-compose up. "
    "Please follow the instructions and be patient until everything is setup")
input_var = input(
    "Please Enter the Full Path to your CEPWARE folder. \n Under Windows it could e.g. be C:\\Workspace\\CEPWARE, "
    "here we need C:\\Workspace)")

strategy = input("Please enter the strategy you want to simulate later. (fire, failure, normal)\n.")
location = input("Please specify where the data should be sent to. (local, fh, test)\n")
if pltfrm == "Windows":
    # input_var = input_var.split(os.sep)
    slash = os.sep
else:
    # input_var = input_var.split(os.altsep)
    slash = os.altsep
source = os.path.join(input_var, "CEPWare", "cepware", "target",
                      "cepware-1.5.jar")
client = docker.from_env()

container = client.containers.get("jobmanager")
containerId = container.id
destination = (containerId + ":" + "/opt/flink/cepware-1.5.jar")

# Function to copy the Apache Flink Jar to the Taskmanager (Docker Apache FLink Container)
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
#Call the requests
# Setup the Subscription from ORION to Cygnus
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "Subscriptions", "post_subscription_cygnus.py"))])
# Setup the Subscription from ORION to Apache Flink
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "Subscriptions", "post_subscription_flink.py"))])
# Create the ORION entities for Room 1 - 5
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "ORION", "post_create_R1.py"))])
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "ORION", "post_create_R2.py"))])
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "ORION", "post_create_R3.py"))])
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "ORION", "post_create_R4.py"))])
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "ORION", "post_create_R5.py"))])
# Register IDAS service group
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "IDAS", "post_provision_service_group.py"))])
# Register IDAS entities for Room 1 -5
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "IDAS", "post_register_IoT-R1.py"))])
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "IDAS", "post_register_IoT-R2.py"))])
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "IDAS", "post_register_IoT-R3.py"))])
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "IDAS", "post_register_IoT-R4.py"))])
subprocess.call(["python", (os.path.join(input_var, "CEPWare", "Scripts", "IDAS", "post_register_IoT-R5.py"))])
print("The infrastructure is up and running.")

print("Starting Datageneration now! Exit with ctrl-c!")
generator_path = os.path.join(input_var, "CEPWare", "Scripts", "cepware-datagenerator-go", "")

if pltfrm == "Windows":
    subprocess.run([generator_path + "cepware-datagenerator-go-windows.exe", "-strategy=" + strategy,
                    "-location=" + location])
elif pltfrm == "Darwin":
    subprocess.run([generator_path + "cepware-datagenerator-go-darwin", "-strategy=" + strategy,
                    "-location=" + location])
else:
    subprocess.run([generator_path + "cepware-datagenerator-go-linux", "-strategy=" + strategy,
                    "-location=" + location])

print("The whole system is up and running. You will now see the Data begin sent.")
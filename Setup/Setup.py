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
    "Please Enter the Full Path to your CEPWARE folder (e.g. C:\\Workspace\\CEPWARE, here we need C:\\Workspace)\n")
strategy = input("Please enter the strategy you want to simulate later. (fire, failure, normal)\n")
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


copy_to(source, destination)
container.exec_run(cmd="flink run ./cepware-1.5.jar", workdir="/opt/flink/")

print("Starting Datageneration now! Exit with ctrl-c!")
generator_path = os.path.join(input_var, "CEPWare", "Scripts", "cepware-datagenerator-go", "")

if pltfrm == "Windows":
    subprocess.run([generator_path + "cepware-datagenerator-go-windows.exe", "-strategy=" + strategy, "-room=1",
                    "-location=" + location])
elif pltfrm == "Darwin":
    subprocess.run([generator_path + "cepware-datagenerator-go-darwin", "-strategy=" + strategy, "-room=2",
                    "-location=" + location])
else:
    subprocess.run([generator_path + "cepware-datagenerator-go-linux", "-strategy=" + strategy, "-room=3",
                    "-location=" + location])

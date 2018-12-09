#!/usr/bin/python

import os
import docker
import tarfile
import platform

pltfrm = platform.system()
print("Welcome to CEPWARE. This is the automated setup. Before you run this script. Please do a docker-compose up. `n Please follow the instructions and be patient until everything is setup")
input_var = input("Please Enter the Full Path to your CEPWARE folder (e.g. C:\Workspace\CEPWARE, here we need C:\Workspace)")
if pltfrm == "Windows":
    #input_var = input_var.split(os.sep)
    slash = os.sep
else :
    #input_var = input_var.split(os.altsep)
    slash = os.altsep
source = os.path.join(input_var, "CEPWARE", "ApacheFlink", "flink-quickstart-scala", "target", "flink-quickstart-scala-1.0-SNAPSHOT.jar")
client = docker.from_env()
container = client.containers.get("jobmanager")
containerId = container.id
destination = (containerId + ":" + "/opt/flink/flink-quickstart-scala-1.0-SNAPSHOT.jar")

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
container.exec_run(cmd="flink run ./flink-quickstart-scala-1.0-SNAPSHOT.jar", workdir="/opt/flink/")



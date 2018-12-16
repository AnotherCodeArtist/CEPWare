#!/usr/bin/python

import sys
import subprocess

Print "Welcome to CEPWARE. This is the automated setup. Before you run this script. Please do a docker-compose up. `n Please follow the instructions and be patient until everything is setup"
input_var = input("Please Enter the Full Path to your CEPWARE folder (e.g. C:\Workspace\CEPWARE, here we need C:\Workspace)")
cepware = "\CEPWARE"
jar= "\CEPWARE\ApacheFlink\flink-quickstart-scala\target\"
jarFile= "flink-quickstart-scala-1.0-SNAPSHOT.jar"
jm = (docker inspect -f '{{.Id}}' jobmanager)

subprocess.call("docker run --rm wappalyzer/cli https://wappalyzer.com", shell=True, stdout=output, stderr=output)
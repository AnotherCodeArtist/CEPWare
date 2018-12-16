#!/usr/bin/python
import docker
import operator

print(
    "This script deletes the whole CEPware infrastructure. Are you sure want to execute it?")
input = input(" 'y' for yes and 'n' for no\n")
if(input == "y"):
	client = docker.from_env()
	
	runningContainers = ["jobmanager", "taskmanager", "cygnus", "idas", "orion", "mongo"]
	images = ["mongo:3.6", "fiware/orion:2.0.0", "fiware/cygnus-ngsi:1.9.0", "telefonicaiot/iotagent-ul:1.7.0", "flink:1.6.1"]
	network = "cepware_cepware"
	volume = "cepware_mongoVol"
	
	
	for container in runningContainers:
		try: 
			delContainer = client.containers.get(container)
			print("Deleting Container: " + container + " ...")
			delContainer.remove(force=True)
	
		except (docker.errors.NotFound, docker.errors.APIError):
			print("Container " + container + " has already been deleted!")
			
	for image in images:
		try:
			delImage = client.images.get(image)
			if delImage != None:
				print("Deleting Image: " + image)
				client.images.remove(image, force=True)
		
		except (docker.errors.ImageNotFound, docker.errors.APIError):
			print("Image " + image + " has already been deleted!")

	try:
		cepwareNW = client.networks.list(filters={'name':network})
		print("Deleting CEPware Network ...")
		deleteNW = cepwareNW[0]
		deleteNW.remove()
	except (docker.errors.APIError, IndexError):
		print("Network Driver: " + network + " has already been deleted!")

	try:
		vol = client.volumes.get(volume)
		print("Deleting Volume")
		vol.remove(force=True)
	except docker.errors.APIError:
		print("Volume: " + volume + " has already been deleted!")

	print("Everything has been deleted!")
else:
	print("Clearing Docker infrastructure has been abborted.")
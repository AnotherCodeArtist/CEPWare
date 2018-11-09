#Delete all containers
docker rm -f $(docker ps -a -q)
#Delete all images
docker rmi -f $(docker images -q)
#Delete all unused volumes
docker volume prune -f
cmd /c pause | out-null
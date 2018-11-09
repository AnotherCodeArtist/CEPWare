Write-Host "Welcome to CEPWARE. This is the automated setup. Please follow the instructions and be patient until everything is setup"
$stw= Read-Host -Prompt "Please Enter the Full Path to your CEPWARE folder (e.g. C:\Workspace\CEPWARE, here we need C:\Workspace)"
$compose =('\CEPWARE')
$jar= ('\CEPWARE\ApacheFlink\flink-quickstart-scala\target\')
$jarFile= ('flink-quickstart-scala-1.0-SNAPSHOT.jar')
$jm=(docker inspect -f '{{.Id}}' jobmanager)
cd $stw$compose
docker-compose up -d
Start-Sleep -s 120
$jm=(docker inspect -f '{{.Id}}' jobmanager)
docker cp $stw$jar$jarFile $jm`:/opt/flink/$jarFile
docker exec -d -t -i $jm flink run /opt/flink/$jarFile
Start-Sleep -s 30
Write-Host "Thank you for your patience. The basic infrastructure is setup. Now you have to send the requests with Postman `n according to the setup instructions."
pause
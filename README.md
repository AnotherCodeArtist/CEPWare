# CEPWare
###### Integrating Apache FLINK Complex Event Processing into the FIWARE platform.

CEPWARE is an Application that integrates [Apache Flink](https://flink.apache.org/) as a Complex Event Processing Unit into the [FIWARE platform](https://www.fiware.org/) as a Docker Environment.

This application has been built as empirical project for bachelor theses at [FH JOANNEUM](https://www.fh-joanneum.at/) for the bachelor's degree programme [Information Management](https://www.fh-joanneum.at/informationsmanagement/bachelor/en/). 

# Teammembers
* @GregorFernbach
* @heiderst16
* @sweiland
* Guidance and Mentor: @AnotherCodeArtist

# Architecture
 CEPWare uses the basic FIWARE infrastructure and therefor contains the following FIWARE components:
* **[Orion Context Broker](https://fiware-orion.readthedocs.io/en/master/)** -> Processes context data and sends it on to the [ORION-Flink-Connector](https://github.com/ging/fiware-cosmos-orion-flink-connector/) and Cygnus Data Sink. Moreover it stores the current context data in the MongoDB.
* **[Cygnus Data Sink](https://readthedocs.org/projects/fiware-cygnus/)** -> Stores Context Data in the MongoDB and therefor creates historical data.
* **[IoT Agent Ultralight 2.0 (IDAS)](https://fiware-iotagent-ul.readthedocs.io/en/latest/)** -> Receveise data from the IoT sensors as HTTP Requests with the Ultralight 2.0 syntax and passes them on to the Orion Context Broker as NGSIv2 events.
* **MongoDB** -> Stores the current and historical Context Data in a NoSQL data base.

Moreover it uses Apache Flink for complex event processing:
Data is sent to Apache Flink by Orion over the [Orion-Flink-Connector](https://github.com/ging/fiware-cosmos-orion-flink-connector/) to the Apache FLink Streaming Jobs.

[Subscriptions](https://fiware-iot-stack.readthedocs.io/en/latest/topics/subcriptions_and_registrations/) are used to send the current context data from Orion to [Cygnus](https://fiware-cygnus.readthedocs.io/en/r5_fiware/cygnus-ngsi/user_and_programmer_guide/connecting_orion/index.html) and the Orion-Flink-Connector.

Our application uses five temperature sensors which simulate five different rooms. These sensors are simulated as either Postman requests or with the provided data-generator script. The appropriate entities are created in [Orion](https://fiware-orion.readthedocs.io/en/1.6.0/user/append_and_delete/index.html), the IoT Agent (IDAS), [Cygnus](https://fiware-cygnus.readthedocs.io/en/latest/cygnus-ngsi/installation_and_administration_guide/name_mappings/index.html) and the mappings to the context broker entities.

The results of the CEP actions are sent to your smartphone via Telegram Notifications.

To see the according requests for subscriptions and setup of Orion and Cygnus Entities go to /Setup/Postman and open the according requests with Postman.

# Requirements:
* Docker needs at least 4 CPU cores assigned. Docker -> Settings -> Advanced -> allocate CPU to 4. Therefor you need at least 2 physical cores.
* Python Scripts under Linux must be run with "sudo" in order to work properly.

# Software Requirements
In order to start the whole system you need the following:
* Docker https://www.docker.com/get-started
* Docker Compose (is installed along with Docker)
* Python 3 https://realpython.com/installing-python/
* Pip3
   * *If you're running Python 3.4+ you have Pip already installed, otherwise [install](https://pip.pypa.io/en/stable/installing/) it. Also you need the following         packages:*
      * pip3 install docker
      * pip3 install request
* Under Windows you can optionally use Kitematic as a grafical user interface for Docker.
* Optionally you can use [Postman](https://www.getpostman.com/downloads/) if you want to set up and test requests manually.
* Telegram Messenger

# Structure
###### Setup
In the folder "Setup" you find everything that is needed to set up the application. Here you have:
* Python Setup Script: This script automatically sets up the CEPware environment.
* Python Data Generator: This script sends generated data according to the specified use case to Apache Flink. It offers three simulation methods:
- Temperature Rising: Simulates that the temperature is rising too fast so that an alert is triggered.
- Minimum and Maximum temperature: Simulates that the absolute maximum temperature (absolute value of 50 degrees and more) and minimum temperature (under 0 degrees) is hit so that warnings will be triggered.
- Failure: Simulates failure of a sensor.
* Python Docker Clear Script: This script deletes the whole CEPware docker environment.
* docker-compose.yml: This yaml file contains the configuration for the docker environment and is used by Docker Compose.

###### Application
Within "Application" you will find the jar files which are needed by Apache Flink to set up the Streaming Jobs.
* MinMax: This jar file contains the StreamingJob 
* TempRising: Simulates that the temperature is rising too fast (.
* Timeout: Simulates a sensor timeout.

###### Sourcecode
Under "Sourcecode" you find the sourcecode of the Apache Flink Streaming Jobs which are written in Scala. It contains the same as the Application folder. The Sourcecode folder is intended if you want to look up code or develop it further.

# Setup
1. To set up everything first install docker, python (and pip) and everything you may optionally need.
2. Afterwards, pull this repo.
3. Go to /Setup, open a shell (cmd/powershell/bash) and run `docker-compose up`. Wait till everything is up and running. The first docker compose up may take around 10 minutes with a solid connection.
4. Go to /Setup and run `python Setup-Script.py`. 
 - This script will prompt you to enter the destination to your CEPWare folder. Enter the absolute path to your CEPWare folder.
 - Afterwards it asks you if you also want to start the automated data script. For yes enter 'y' for no everything else.
5. If you didn't start the data generator through the set up script, go to /Setup and run `python Data-Generator.py'.
 - This script will prompt you to enter the desired simulation method. For Fire 'fire', Failure 'failure', minmax 'minmax'.
6. Finally to delete CEPWare go to /Setup and run `python Clear-Docker.py`. This will delete the whole CEPWare Environment.

## Telegram CEPWare Channel:
1. Install Telgram Messenger and create an account (if you don't already have one). [Telegram Apps](https://telegram.org/apps)
2. Join the [channel](https://t.me/Cepware).
3. Boom, you should get your notifications in there (if you send appropriate data)!

## Create Your own Channel and Bot:
This Approach describes how you can alter the Sourcecode to send your own Messages to your own Telegram Channel
1. Create a new Telegram bot with the Help of Botfather (see https://core.telegram.org/bots for help)
2. Note the token you get from Botfather for your new Bot
3. Create a new public Channel in Telegram
4. Now add your created Bot to the Channel and give him Admin privileges
5. In the Sourcecode, you need to send a Request to a URL where you insert the token of your Bot and your Channel ID
(https://api.telegram.org/botINSERT_BOT_KEY/sendMessage?chat_id=@CHANNEL&text=)
6. You can append your message at the end of the url after "text="

[![Waffle.io - Columns and their card count](https://badge.waffle.io/AnotherCodeArtist/CEPWare.svg?columns=all)](https://waffle.io/AnotherCodeArtist/CEPWare)

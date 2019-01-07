# CEPWare
###### Integrating Apache FLINK Complex Event Processing and FIWARE

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

Subscriptions are used to send the current context data from Orion to Cygnus and the Orion-Flink-Connector.

# Requirements:
* Docker needs at least 4 CPU cores assigned. Docker -> Settings -> Advanced -> allocate CPU to 4.
* Python Scripts under Linux must be run with "sudo" in order to work properly.

# Software Requirements
In order to start the whole system you need the following:
* Docker https://www.docker.com/get-started
* Docker Compose (is installed along with Docker)
* Python 3 https://realpython.com/installing-python/
* Pip3
   * *If you're running Python 3.4+ you have Pip already installed, otherwise install it. Also you need the following         packages:*
      * pip3 install docker
      * pip3 install request
* Under Windows you can optionally use Kitematic as a grafical user interface for Docker.

# Structure
In the folder "Setup" you find everything that is needed to set up the application. Here you have:
* Python Setup Script: This script automatically sets up the CEPware environment.
* Python Data Generator: This script sends generated data according to the specified use case to Apache Flink.
* Python Docker Clear Script: This script deletes the whole CEPware docker environment.
* docker-compose.yml: This yaml file contains the configuration for the docker environment and is used by Docker Compose.

Within "Application" you will find the jar files which are needed by Apache Flink to set up the Streaming Jobs.
* MinMax: This jar file contains the StreamingJob which simulates absolute maximum and minimum temperature which kick off warning messages.
* Fire: Simulates a fire use case.
* Testing: Simulates a testing use case.
* Timeout: Simulates a sensor timeout.

Under "Sourcecode" you find the sourcecode of the Apache Flink Jobs which are written in Scala. It contains the following Jobs:
* MinMax
* Fire
* Test
* Timeout

#Setup
[![Waffle.io - Columns and their card count](https://badge.waffle.io/AnotherCodeArtist/CEPWare.svg?columns=all)](https://waffle.io/AnotherCodeArtist/CEPWare)

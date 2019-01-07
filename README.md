# CEPWare
Integrating Apache FLINK Complex Event Processing and FIWARE

# Teammembers
* @GregorFernbach
* @heiderst16
* @sweiland

# Requirements:
* Docker needs at least 4 CPU cores assigned. Docker -> Settings -> Advanced -> allocate CPU to 4.
* Python Scripts under Linux must be run with "sudo" in order to work properly.

# Setup
In order to start the whole system you need the following:
* Docker https://www.docker.com/get-started
* Docker Compose
* Python 3 https://realpython.com/installing-python/
* Pip3
   * *If you're running Python 3.4+ you have Pip already installed, otherwise install it. Also you need the following         packages:*
      * pip3 install docker
      * pip3 install request
* Under Windows you can optionally use Kitematic as a grafical user interface for Docker.

In the folder "Setup" you find everything that is needed to set up the application. Here you have:
* Python Setup Script
* Python Data Generator
* docker-compose.yml which contains the configuration for the docker environment

Under "Sourcecode" you find the sourcecode of the Apache Flink Jobs which are written in Scala. It contains the following Jobs:
* MinMax
* Fire
* Test
*

[![Waffle.io - Columns and their card count](https://badge.waffle.io/AnotherCodeArtist/CEPWare.svg?columns=all)](https://waffle.io/AnotherCodeArtist/CEPWare)

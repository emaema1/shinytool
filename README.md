# shinytool
A shinytool to manage my server.py instances

shinytool is a simple python command line utility to manage instances and microservers deployed in shinycloud.
It leverages the provided rest API to allow visualization of the deployed instances, their health state
based on configured memory and cpu usage, and also allows you verify a sufficient number of healthy instances is deployed for 
all your microservers 

## Installation
shinytool depends on the following libraries, to be installed through pip:

json
requests
argparse
pprint
os
time
collections

It has only been tested with Python 3.6, so you should make sure that you have the correct Python version

## Usage
You'll just need to run shinytool.sh and pass the required parameters for your use case:
Manage shiny microservices

positional arguments:
  server                REST Api server:port, e.g. 127.0.0.1:9999

optional arguments:
  -h, --help            show this help message and exit
  --memoryHealth MEMORYHEALTH
                        memory health percentage threshold. Defaults to 75.
                        e.g --memoryHealth 80
  --cpuHealth CPUHEALTH
                        memory health percentage threshold. Defaults to 75.
                        e.g --cpuHealth 80
  --healthyInstances HEALTHYINSTANCES
                        minimum number of instances required for a service to
                        be healthy. Defaults to 2. e.g --healthyInstances 3
  --summary             Prints a list of the all the running instances for all
                        services
  --serviceStats SERVICESTATS
                        Prints a list of all the instances running the
                        specified service. e.g --serviceStats TimeService
  --healthcheck         Prints a list of all the services with a low number of
                        healthy instances
  --monitorService MONITORSERVICE
                        linux top style resource monitoring for a specified
                        server instances. e.g --monitorService TimeService

## Examples

print a list of all the running instances for all services, with default health treesholds
python shinytool.py 127.0.0.1:9999 --summary

----------------------
print a list of all the running instances for all services, with custom cpu and memry threshold
python shinytool.py 127.0.0.1:9999 --summary --cpuHealth 80 --memoryHealth 80

The above will only flag as unhealty instances with either more than 80% used cpu or more than 80% used memory

----------------------
python shinytool.py 127.0.0.1:9999 --healthcheck --cpuHealth 80 --memoryHealth 80  --healthyInstances 3

The above will print a list of the microservices that have less than 3 healthy instances,
where the health treshold for an instance are 80% memory and 80%cpu

----------------------
python shinytool.py 127.0.0.1:9999 --monitorService TimeService --cpuHealth 60 --memoryHealth 80 

will give top() style realtime view of all the instances deployed for a service, and their health status

----------------------
python shinytool.py 127.0.0.1:9999 --serviceStats TimeService --cpuHealth 60 --memoryHealth 80 --healthyInstances 8

This command will give you an average of the memory and cpu utilization across instances, and if the service health match
the given parameters

## Architecture and future improvements
There are quite a few low hanging fruits, like adding sorting to the print functions, and allow shinytool to operate
on a specified subset of services, as opposed to one or all.
There is also some minor streamlining such as specifying default values for cpuHealth,memoryHealth and healthyInstances as arguments
of argparse instead than global variables

In the medium term it would be useful to rewrite the printing functions as the the moment they are strongly dependent 
on the layout of the information returned by the api.
Although the api is unlikely to change it's replies format in the short term a more general print function would future proof
shinytool quite a bit.

A very important change that would be useful to streamline shinytool, and make it more elegant, would be rewriting it to make use of classes, instead 
than extensively rely on lists and dictionaries.
This option although tempting has not been selected due to the time limit in developing shinytool, that steered my choice 
toward structures I'm more experienced with

Eventually in the medium/long term a configuration file may be created, to save preferred settings and the possibility to save instances and services state,
 to keep track of changes.

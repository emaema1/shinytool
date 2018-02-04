# DevOps challenge


## Abstract

You have just joined a shiny new startup that doesn’t have any prior devops experience. They have deployed a bunch of microservices in the cloud but don’t have monitoring or any way of determining how many instances are running. In an attempt to organise your deployments you decide to write a command line tool that will leverage your cloud provider's API.

## Challenge

The tool should have multiple commands.

Depending on which command is ran, it should:

1. Print running services to stdout (similar to the table below)
1. Print out average CPU/Memory of services of the same type
1. Flag services which have fewer than 2 healthy instances running
1. Have the ability to track and print CPU/Memory of all instances of a given service over time (until the command is stopped, e.g. ctrl + c).

For example, (1) should print out something like:

           IP            Service          Status     CPU   Memory
       ­­­­­­­­­­­ ­­­­­­­­­­­­­­­­­­­­ ­­­­­­­­­­­ ­­­­­ ­­­­­­­­
        10.22.11.1   PermissionsService   Healthy     28%   32%
        10.22.11.2   AuthService          Healthy     14%   10%
        10.22.11.3   StorageService       Healthy     9%    5%
        10.22.11.4   TimeService          Unhealthy   95%   85%
        10.22.11.5   GeoService           Healthy     35%   55%

(But feel free to be creative!)

## Assumptions:

* Your cloud provider offers an API for fetching all running servers.
* The same service also allows you to query a given IP for simple stats.

You should have been provided with a simple `Python2.7` server which two endpoints. You can run it as follows:

      # start the server
      python server.py <port­-to-­serve-­on>

      # query the API to list the servers
      $ curl localhost:<port>/servers
      ["10.22.11.121", "10.22.11.120", "10.22.11.123", "10.22.11.122", ...]

      # retrieve info for a given server
      $ curl localhost:<port>/10.22.11.121
      {"cpu": "61%", "service": "StorageService", "memory": "4%"}

## Deliverables:

* An archive of a `git` repository that contains the complete source code of your program, written in either Python, Go, NodeJS or Ruby.
* You should include a `README.md` file explaining some of the choices you’ve made, tradeoffs and future improvements.
* Documentation on how to build and/or run your program.
* Feel free to use open source third party libraries. However, you should not assume that these libraries will be globally installed on the system; you should provide instructions on how to fetch them in the `README.md`.

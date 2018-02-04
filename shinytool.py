import json
import requests
import argparse
import pprint
import os
from time import sleep
from collections import defaultdict

pp = pprint.PrettyPrinter(indent=2)
minHealtyServiceInstances = 8
#server = "127.0.0.1:9999"



def apiReq (server,endpoint="servers"):
    """Takes a server and a query endpoint, connects or handle exception. If succesfull
    decodes the retrieved json data and returns it as a python data structure.

    Required Parameters:
        server - Api Server to connect to, formatted as ip:port. Doesn't support https at the moment
        endpoint - Api endpoint to call
    """
    apiUri = 'http://' + server + '/' + endpoint
    apiResponse = requests.get(apiUri)
    if apiResponse.ok:
        return json.loads(apiResponse.content)
    else:
        apiResponse.raise_for_status()


def getInstanceStats (instanceId):
    """Retrieves stats for a specific instance, identified by the instance api id
    Also marks the instance as healty or not depending on resource usage.

    Required Parameters:
        instanceId - Expects a valid instance id as per the api documentation. String
    """
    result = apiReq(server, instanceId)
    #In the current api version the ip is passed as instance id, and is not part of the retrieved values
    result.update({'ip': instanceId})

    #Below we strip the % sign and convert memory and cpu to a number to compare usage
    if float(result['memory'].strip(' \t\n\r%')) < 75 and float(result['cpu'].strip(' \t\n\r%')) < 75:
        result.update({'status': 'healthy'})
    else:
        result.update({'status': 'unhealthy'})
    return result


#retrieves data for a specified service instances. If the service is not specified retrieves all instances
def getServiceStats (service=None):
    """Retrieves instances for a specified service, or for all services,
    and returns it as a list of dictionaries.

    Optional Parameters:
        service - Expects a valid service id as per api documentation. String.
        If not passed defaults to all services
    """
    result=[]
    instanceIds = apiReq(server, 'servers')
    #We use defaultdict as we don't know the serviceIds in advance
    instances = defaultdict(list)
    for instanceId in instanceIds:
        instance = getInstanceStats(instanceId)
        instances[instance['service']].append(instance)
    #If no service has been specified pass all instances
    if not service:
        for serviceId in instances:
            result = result + (instances[serviceId])
    else:
        result = instances[service]
    return result


#expects a list of instances, separates them by service and checks if enough instance for each service are healty.
#Return a dictionary such as { 'service1':'healty','service2': 'unhealty'}
def getServiceHealth (serviceInstances = dict):
    """Scans the provided list of instances and return either an "healthy" or "unhealty" value for each service,
    depending on how many healty instances are running.

    Required Parameters:
    serviceInstances - Expects a list of instances, as retuned by getServiceStats. List of dictionaries.
    They can belong to multiple services, the check will be carried out separately for each service
    """
    serviceHealthSummary = {}
    #We don't know how many services are part of the instance list
    healtyServiceInstances = defaultdict(int)
    for serviceInstance in serviceInstances:
        if serviceInstance['status'] == 'healthy':
            healtyServiceInstances[serviceInstance['service']] += 1

    for service in healtyServiceInstances:
        if healtyServiceInstances[service] >= minHealtyServiceInstances:
            serviceHealthSummary[service] = 'healthy'
        else:
            serviceHealthSummary[service] = 'unhealty'
    return serviceHealthSummary


#Get the average resource usage across the instances, number of instances and status of the service
#Returns a dictionary
def getServiceStatus (service):
    """ Calculates an average of the service resource usage and health level
    and returns it as a dictionary

    Required Parameters:
    service - Expects a valid service id as per api documentation. String.
    """
    serviceInstances = getServiceStats(service)
    serviceMemory = 0
    serviceCpu = 0
    for instance in serviceInstances:
        serviceMemory += int(instance['memory'].strip(' \t\n\r%'))
        serviceCpu += int(instance['cpu'].strip(' \t\n\r%'))
    serviceMemory = serviceMemory / len(serviceInstances)
    serviceCpu = serviceCpu / len(serviceInstances)
    serviceState = {'service': service, 'cpu': serviceCpu, 'memory': serviceMemory, 'status': getServiceHealth(serviceInstances)[service], 'instances': len(serviceInstances)}
    return serviceState


def printInstances(instanceList):
    """ Expects a list of instances. Prints them in a nicely formatted table

    Required Parameters:
    instanceList - Expects a list of instances, as returned by getServiceStats. List of dictionaries.

    """
    print('{:16} {:25} {:8} {:8}'.format('ip','service','cpu','memory','status'))
    print('------------------------------------------------------------')
    for item in instanceList:
        row = '{:16} {:25} {:8} {:8} {:8}'.format(item['ip'],item['service'], item['cpu'], item['memory'], item['status'])
        print (row)

def printServiceStatus(serviceStatus):
    """ Expects a service status. Prints it in a nicely formatted table
    Required Parameters:
    serviceStatus - Expects a serviceStatus dictionary, as returned by getServiceStatus. Dictionary.
    """
    print('{:25} {:8} {:8} {:8}'.format('service', 'cpu', 'memory','status'))
    print('------------------------------------------------------------')
    row = '{:25} {:^8.2f} {:^8.2f} {:8}'.format(serviceStatus['service'], serviceStatus['cpu'], serviceStatus['memory'], serviceStatus['status'])
    print (row)

def printServiceHealth(serviceHealthSummary):
    """ Expects a dictionary containing a key for each service pointing to the service health state.
     Prints it in a nicely formatted table

    Required Parameters:
    serviceHealthSummary - Expects a serviceHealthSummary dictionary, as returned by getServiceHealth. Dictionary.
    """
    print('{:25} {:16}'.format('service','status'))
    print('---------------------------------')
    for service in serviceHealthSummary:
        row = '{:25} {:16}'.format( service, serviceHealthSummary[service] )
        print (row)


parser = argparse.ArgumentParser(description='Manage shiny microservices')

group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument(
    'server',
    help='REST Api server:port, e.g. 127.0.0.1:9999',
    #required=True
)
group.add_argument(
    '--summary',
    help='Prints a list of the all the running instances for all services',
    action="store_true",
    required=False
)
group.add_argument(
    '--serviceStats',
    help='Prints a list of all the instances running the specified service. e.g --serviceStats TimeService',
    required=False
)
group.add_argument(
    '--healthcheck',
    help='Prints a list of all the services with a low number of healthy instances',
    action="store_true",
    required=False
)
group.add_argument(
    '--monitorService',
    help='linux top style resource monitoring for a specified server instances. e.g --monitorService TimeService',
    required=False
)

args = parser.parse_args()
server = args.server


if args.summary:
    printInstances(getServiceStats())

if args.healthcheck:
    instances = getServiceStats()
    printServiceHealth(getServiceHealth(instances))

if args.serviceStats:
    printServiceStatus(getServiceStatus(args.serviceStats))

if args.monitorService:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        printInstances(getServiceStats(args.monitorService))
        sleep(5)


#if args.monitorService:

#print(vars(args))
#print(getServiceInstances()['StorageService'])
#print(getServiceInstances())

#pp.pprint(getInstanceStats(instances['StorageService']))
#print(getServiceStats('StorageService'))
#colPrint(getServiceStats('PermissionsService'))
#print(getServiceStatus('PermissionsService'))
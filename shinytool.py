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
endpoint = "servers"


def apiReq (server,endpoint):
    apiUri = 'http://' + server + '/' + endpoint
    apiResponse = requests.get(apiUri)
    if apiResponse.ok:
        return json.loads(apiResponse.content)
    else:
        apiResponse.raise_for_status()


# Retrieve stats for a specific instance, identified by the ip
# Also checks that resource usage is within expected bound and mark the instance status appropiately
def getInstanceStats (instanceId):
    result = apiReq(server, instanceId)
    result.update({'ip': instanceId})
    #Below we strip the % sign and convert memory and cpu to a number to compare usage
    if float(result['memory'].strip(' \t\n\r%')) < 75 and float(result['cpu'].strip(' \t\n\r%')) < 75:
        result.update({'status': 'healthy'})
    else:
        result.update({'status': 'unhealthy'})
    return result


#retrieves data for a specified service instances. If the service is not specified retrieves all instances
def getServiceStats (service=None):
    result=[]
    instanceIds = apiReq(server, 'servers')
    instances = defaultdict(list)
    for instanceId in instanceIds:
        instance = getInstanceStats(instanceId)
        #print(instance)
        instances[instance['service']].append(instance)
    #print(instances)
    if not service:
        for serviceId in instances:
            result = result + (instances[serviceId])
    else:
        result = instances[service]
    #print (result)
    return result


#expects a list of instances, separates them by service and checks if enough instance for each service are healty.
#Return a dictionary such as { 'service1':'healty','service2': 'unhealty'}
def checkServiceHealth (serviceInstances = dict):
        result = defaultdict(dict)
        healtyServiceInstances = defaultdict(int)
        for serviceInstance in serviceInstances:
            if serviceInstance['status'] == 'healthy':
                #print(serviceInstance)
                healtyServiceInstances[serviceInstance['service']] += 1

        for service in healtyServiceInstances:
            if healtyServiceInstances[service] >= minHealtyServiceInstances:
                result[service] = 'healthy'
            else:
                result[service] = 'unhealty'
        return result


#Get the average resource usage across the instances, number of instances and status of the service
#Returns a dictionary
def getServiceStatus (service):
    serviceStats = getServiceStats(service)
    serviceMemory = 0
    serviceCpu = 0
    for instance in serviceStats:
        serviceMemory += int(instance['memory'].strip(' \t\n\r%'))
        serviceCpu += int(instance['cpu'].strip(' \t\n\r%'))
    serviceMemory = serviceMemory / len(serviceStats)
    serviceCpu = serviceCpu / len(serviceStats)
    #servicesHealth =
    serviceState = {'service': service, 'cpu': serviceCpu, 'memory': serviceMemory, 'status': checkServiceHealth(serviceStats)[service], 'instances': len(serviceStats)}
    return serviceState


def printInstances(data):
    print('{:16} {:20} {:8} {:8}'.format('ip','service','cpu','memory','status'))
    print('------------------------------------------------------------')
    print(data)
    for item in data:
        row = '{:16} {:20} {:8} {:8} {:8}'.format(item['ip'],item['service'], item['cpu'], item['memory'], item['status'])
        print (row)

def printServiceStatus(data):
    print('{:25} {:8} {:8} {:8}'.format('service', 'cpu', 'memory','status'))
    print('------------------------------------------------------------')
    row = '{:25} {:^8.2f} {:^8.2f} {:8}'.format(data['service'], data['cpu'], data['memory'],data['status'])
    print (row)

def printServiceHealth(data):
    print (data)
    print('{:16} {:20}'.format('service','status'))
    print('---------------------------------')
    for service in data:
        row = '{:16} {:16}'.format( service, data[service] )
        print (row)


parser = argparse.ArgumentParser(description='Manage shiny microservices')

group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument(
    'server',
    help='REST Api server:port , e.g. 127.0.0.1:9999',
    #required=True
)
group.add_argument(
    '--summary',
    help='Prints a list of the all the running instances',
    action="store_true",
    required=False
)
group.add_argument(
    '--serviceStats',
    help='Prints a list of all the instances running the specified service',
    required=False
)
group.add_argument(
    '--healthcheck',
    help='Prints a list of all the services with a dangerously low number of instances',
    action="store_true",
    required=False
)
group.add_argument(
    '--monitorService',
    help='linux top style resource monitoring for a specified server instances',
    required=False
)

args = parser.parse_args()
server = args.server


if args.summary:
    #colPrint(getServiceStats())
    instances = getServiceStats()
    printInstances(instances)
    #print(format_as_table (instances,keys,headers))

if args.healthcheck:
    instances = getServiceStats()
    printServiceHealth(checkServiceHealth(instances))
    print(checkServiceHealth(instances))

if args.serviceStats:
    printServiceStatus(getServiceStatus(args.serviceStats))
    print(getServiceStatus(args.serviceStats))
if args.monitorService:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        colPrint(getServiceStats(args.monitorService))
        sleep(5)


#if args.monitorService:

#print(vars(args))
#print(getServiceInstances()['StorageService'])
#print(getServiceInstances())

#pp.pprint(getInstanceStats(instances['StorageService']))
#print(getServiceStats('StorageService'))
#colPrint(getServiceStats('PermissionsService'))
#print(getServiceStatus('PermissionsService'))
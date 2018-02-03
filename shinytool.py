import json
import requests
import argparse
import pprint
from collections import defaultdict

pp = pprint.PrettyPrinter(indent=2)
#server = "127.0.0.1:9999"
endpoint = "servers"

def apiReq (server,endpoint):
    apiUri = 'http://' + server + '/' + endpoint
    apiResponse = requests.get(apiUri)
    if apiResponse.ok:
        return json.loads(apiResponse.content)
    else:
        apiResponse.raise_for_status()

def getinstanceList():
    return

#def getServiceInstances ():
#    #instances = defaultdict(lambda: defaultdict(dict))
#    instances = defaultdict(list)
#    ids = apiReq(server, 'servers')
#    for id in ids:
#        instance = apiReq(server, id)
#        instances[instance['service']].append(id)
#   return instances

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

def getServiceStatsAverage (service):
    serviceStats = getServiceStats(service)
    serviceRam = 0
    serviceCpu = 0
    for instance in serviceStats:
        serviceRam += float(instance['memory'].strip(' \t\n\r%'))/len(serviceStats)
        serviceCpu += float(instance['cpu'].strip(' \t\n\r%'))/len(serviceStats)
    return serviceRam
   # return instances
   # for instanceId in instances:
   #     result.append(getInstanceStats(instanceId))
   # return result

def colPrint(data):
    print('{:15} {:20} {:6} {:6}'.format('ip','service','cpu','memory'))
    print('------------------------------------------------------------')
    for item in data:
        row = '{:15} {:20} {:6} {:6} {:8}'.format(item['ip'],item['service'], item['cpu'], item['memory'], item['status'])
        print (row)


parser = argparse.ArgumentParser(description='Manage shiny microservices')
parser.add_argument(
    '--server',
    help='REST Api server url, e.g. http://127.0.0.1:9999/',
    required=True
)
parser.add_argument(
    '--summary',
    help='Prints a list of the all the running instances stats',
    action="store_true",
    required=False
)
parser.add_argument(
    '--serviceStats',
    help='Prints a list of all the instances running the specified service',
    required=False
)
parser.add_argument(
    '--healthcheck',
    help='Prints a list of all the services with a dangerously low number of instances',
    action="store_true",
    required=False
)
parser.add_argument(
    '--monitorService',
    help='linux top style resource monitoring for a specified server instances',
    required=False
)

args = parser.parse_args()
#server = vars(args)['server']
server = args.server
#print(vars(args))
#print(getServiceInstances()['StorageService'])
#print(getServiceInstances())



#pp.pprint(getInstanceStats(instances['StorageService']))
#print(getServiceStats('StorageService'))
colPrint(getServiceStats())
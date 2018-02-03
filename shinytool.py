import json
import requests
import argparse
import pprint
from collections import defaultdict

pp = pprint.PrettyPrinter(indent=2)
server = "127.0.0.1:9999"
endpoint = "servers"

def apiReq (server,endpoint):
    apiUri = 'http://' + server + '/' + endpoint
    apiResponse = requests.get(apiUri)
    if apiResponse.ok:
        return json.loads(apiResponse.content)
    else:
        apiResponse.raise_for_status()

def getServiceInstances ():
    #instances = defaultdict(lambda: defaultdict(dict))
    instances = defaultdict(list)
    ids = apiReq(server, 'servers')
    for id in ids:
        instance = apiReq(server, id)
        instances[instance['service']].append(id)
    return instances

def getInstanceStats (instanceId):
    result = apiReq(server, instanceId)
    result.update({'ip': instanceId})
    return result

def getServicesStats (instances):
    result = []
    for instanceId in instances:
        result.append(getInstanceStats(instanceId))
    return result

def colPrint(data):
    print('{:15} {:20} {:6} {:6}'.format('ip','service','cpu','memory'))
    print('--------------------------------------------------')
    for item in data:
        row = '{:15} {:20} {:6} {:6}'.format(item['ip'],item['service'], item['cpu'], item['memory'])
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
    '--healtcheck',
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
instances = getServiceInstances()




#pp.pprint(getInstanceStats(instances['StorageService']))
colPrint(getServicesStats(instances['StorageService']))
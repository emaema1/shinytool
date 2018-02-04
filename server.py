#/usr/bin/env python2.7

import BaseHTTPServer
import hashlib
import json
import random
import re
import SimpleHTTPServer
import sys

NUM_SERVERS = 150
SERVER_SET = set(['10.22.11.%d' % i for i in range(1, NUM_SERVERS + 1)])
IP_REGEX = r'/10\.22\.11\.[0-9]{1,3}$'
SERVICES = ['PermissionsService',
            'AuthService',
            'StorageService',
            'TimeService',
            'GeoService',
            'TicketService',
            'GroupService',
            'NotificationService',
            'UserService',
            'EmailService']


def _server_stats(ip):
    service_idx = int(hashlib.md5(ip).hexdigest(), 16) % len(SERVICES)
    service_name = SERVICES[service_idx]
    return {
        'cpu': '%d%%' % random.randint(0, 100),
        'memory': '%d%%' % random.randint(0, 100),
        'service': service_name
    }


class APIHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def _invalid_endpoint(self):
        self.send_response(400)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Invalid IP'}))

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data))

    def do_GET(self):
        ip_match = re.match(IP_REGEX, self.path)
        if self.path == '/servers':
            self._json(list(SERVER_SET))
        elif ip_match:
            ip = ip_match.group().replace('/', '')
            if ip not in SERVER_SET:
                self._invalid_endpoint()
            else:
                self._json(_server_stats(ip))
        else:
            self._invalid_endpoint()


def main(args):
    if len(args) != 2:
        print 'Must specify the port on which to run.'
        sys.exit(1)

    try:
        port = int(args[1])
    except ValueError:
        print 'Must specify an integer value.'

    httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', port), APIHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    main(sys.argv)

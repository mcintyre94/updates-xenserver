#!/usr/bin/env python

import configparser
import HostAnalysis
import json
import requests
import time

url_config = configparser.ConfigParser()
url_config.read('urls.cfg')
read_hosts_url = url_config.get('urls', 'read_url')
write_hosts_url = url_config.get('urls', 'write_url')

config = configparser.ConfigParser()
config.read('credentials.cfg')
username = config.get('host', 'username')
password = config.get('host', 'password')
# TODO: support for a username/password per host

sleep_time = 10

def get_hosts():
    print("Getting hosts...")
    return requests.get(read_hosts_url).json()


def handle_host(host):
    print("Analysing host %s..." % host)
    host_url = host['host']
    results = HostAnalysis.analyse_host(host_url, username, password)
    
    host.update(results) # Only change fields we've changed
    host['pending'] = True # Ensure this row gets processed

    requests.post(write_hosts_url, json=host)
    print("posted...")


def analyse_all_hosts():
    hosts = get_hosts()
    print(hosts)

    for host in hosts:
        handle_host(host)


def main():
    while(True):
        analyse_all_hosts()
        time.sleep(sleep_time)
    

if __name__ == '__main__':
   main() 

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
    read_key = config.get('apis', 'read_key')
    params = {
        'subset': 'pending',
        'code': read_key
    }
    return requests.get(read_hosts_url, params=params).json()


def should_analyse_host(host):
    # TODO: Needs to be smarter about when hosts should be re-analysed
    return 'host_version' not in host or 'installed_updates' not in host


def handle_host(host):
    print("Analysing host %s..." % host['host'])
    host_url = host['host']
    results = HostAnalysis.analyse_host(host_url, username, password)
    
    host.update(results) # Only change fields we've changed
    host['pending'] = True # Ensure this row gets processed

    print("posting analysed host...")
    write_key = config.get('apis', 'write_key')
    requests.post(write_hosts_url, json=host, params={'code': write_key})
    print("posted...")


def analyse_all_hosts():
    hosts = get_hosts()
    hosts = list(filter(should_analyse_host, hosts))
    print(hosts)

    for host in hosts:
        handle_host(host)


def main():
    while(True):
        analyse_all_hosts()
        time.sleep(sleep_time)
    

if __name__ == '__main__':
   main() 

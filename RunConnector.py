#!/usr/bin/env python

import configparser
import HostAnalysis
import requests

def get_hosts():
    # TODO: use a cloud call to get the hosts
    return ['http://cl01-09.xenrt.citrite.net', 'http://xrtuk-12-06.xenrt.citrite.net']


def handle_host(host, username, password, api_url):
    results = HostAnalysis.analyse_host(host, username, password)
    print(results)

    requests.post(api_url, json=results)


def main():
    hosts = get_hosts()
    print(hosts)

    # TODO: support for a username/password per host
    config = configparser.ConfigParser()
    config.read('credentials.cfg')
    username = config.get('host', 'username')
    password = config.get('host', 'password')
    api_url = config.get('submitAPI', 'url')
    print(api_url)

    for host in hosts:
        handle_host(host, username, password, api_url)
    

if __name__ == '__main__':
   main() 

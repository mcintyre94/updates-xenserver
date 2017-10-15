import json
import os
import requests
import subprocess
import time

deployment_url = 'http://cm-test-flask-svc.azurewebsites.net'  # Azure for deployed
#deployment_url = 'http://localhost:5000' # Localhost for dev
api_url_base = "%s/api/cc/get-hosts" % deployment_url
post_data_url = "%s/api/cc/set-host-data" % deployment_url

last_seen_file = 'last-seen.txt'

if not os.path.exists(last_seen_file):
    last_seen = 0
else:
    last_seen = int(open(last_seen_file, 'r').readline())

while(True):
    time.sleep(2)

    # Call the API
    payload = {'last-seen': last_seen}
    print(api_url_base, payload)
    r = requests.get(api_url_base, params=payload)

    new_hosts = r.json()

    hostname_ids = {}

    for new_host in new_hosts:
        if new_host['id'] > last_seen:
            last_seen = new_host['id']

        hostname_ids[new_host['hostname']] = str(new_host['id'])
    
    if os.path.exists(last_seen_file):
        append_write = 'a'  # Exists, so append
    else:
        append_write = 'w' # Make a new file

    with open(last_seen_file, 'w') as last_seen_buffer:
        last_seen_buffer.write(str(last_seen))

    hostnames = hostname_ids.keys()
    if not hostnames:
        continue

    print(hostnames)

    host_data = subprocess.check_output(["python", "update-xs.py"] + hostnames)
    if(host_data.startswith('Failed')):
        print("Error from update-xs.py : %s" % host_data)
        continue

    print("Response looks good, submitting!")
    requests.post(post_data_url, json=host_data)
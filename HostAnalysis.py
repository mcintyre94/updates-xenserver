#!/usr/bin/env python

"""
A simple script to get the host version and installed updates
This should be the only script that can make calls on the host and is given credentials
"""

import argparse
import XenAPI

def get_session(host, username, password):
    session = XenAPI.Session(host)
    session.login_with_password(username, password)
    return session


def get_server_version(session):
    host_ref = session.xenapi.host.get_all()[0]
    host = session.xenapi.host.get_record(host_ref)
    host_product_version = host['software_version']['product_version']
    return host_product_version


def get_installed_updates(session):
    patch_refs = session.xenapi.pool_update.get_all_records()
    updates = []
    for patch_ref in patch_refs:
        patch = session.xenapi.pool_update.get_record(patch_ref)
        updates.append(patch['name_label'])
    return list(set(updates)) # Ensure unique


def analyse_host(host, username, password):
    session = get_session(host, username, password)
    server_version = get_server_version(session)
    installed_updates = get_installed_updates(session)

    response = {
        "host_version": server_version,
        "installed_updates": installed_updates
    }

    return response

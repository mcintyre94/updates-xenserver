#!/usr/bin/env python

"""
A simple script to get the missing updates for a host
Input:
{
    "host",
    "server_version":,
    "installed_updates"
}
"""

import requests
import sys
import urllib.parse
import xml.etree.ElementTree as ET

def get_track(host_version):
    if host_version.startswith('7.1'):
        return 'CU'
    else:
        return 'CR'


def get_cfu_content():
    citrix_update_url = "https://updates.xensource.com/XenServer/updates.xml"
    r = requests.get(citrix_update_url)
    return ET.fromstring(r.text)


def get_patches_for_ele(cfu_root, version_ele):
    minimal_patch_eles = version_ele.findall('./minimalpatches/patch')
    
    patches = []
    for minimal_patch_ele in minimal_patch_eles:
        uuid = minimal_patch_ele.get('uuid')

        patch_ele = cfu_root.find('./patches/patch[@uuid="%s"]' % uuid)
        patches.append({
            'name': patch_ele.get('name-label'), 
            'description': patch_ele.get('name-description'),
            'uuid': patch_ele.get('uuid'),
            'update_type': patch_ele.get('update-type')
        })
    
    return patches


def get_patches_for_version(cfu_root, version):
    version_ele = cfu_root.find('./serverversions/version[@value="%s"]' % version)
    if version_ele is None:
        return []
    
    return get_patches_for_ele(cfu_root, version_ele)


def get_missing_patches(all_patches, installed_patches):
    missing_patches = []
    for patch in all_patches:
        if patch['name'] not in installed_patches:
            missing_patches.append(patch)

    return missing_patches


def get_latest_server_version(cfu_root, track):
    # TODO: how is this latest/latestcr meant to work? For now, hacks
    if track=='CU':
        return None # Presented as an update instead

    else:
        # Hardcode Falcon for now for demo purposes
        return cfu_root.find('./serverversions/version[@value="7.2.0"]') 

def get_new_server_version(version_ele, current_version):
    new_server_version = {}
    if version_ele is None:
        return new_server_version

    latest_server_version = version_ele.get('value')
    if latest_server_version != current_version:
        new_server_version['name'] = version_ele.get('name')
        new_server_version['uuid'] = version_ele.get('uuid')

    return new_server_version


def get_new_version_patches(cfu_root, missing_patches):
    new_version_patches = []
    for patch in missing_patches:
        if patch['update_type'] == 'Service Pack':
            # Get the matching version
            uuid = patch['uuid']
            new_version_ele = cfu_root.find('./serverversions/version[@patch-uuid="%s"]' % uuid)
            new_version_patches = get_patches_for_ele(cfu_root, new_version_ele)

    return new_version_patches


def main(host_version, installed_updates):
    track = get_track(host_version)

    cfu_root = get_cfu_content()
    
    results = {}

    results['current_version'] = host_version
    results['track'] = track

    # current_version_patches
    all_patches_for_version = get_patches_for_version(cfu_root, host_version)
    missing_patches = get_missing_patches(all_patches_for_version, installed_updates)
    results['current_version_patches'] = missing_patches

    # new_server_version
    latest_server_version_ele = get_latest_server_version(cfu_root, track)
    new_server_version = get_new_server_version(latest_server_version_ele, host_version)
    results['new_server_version'] = new_server_version

    # new_version_patches
    # For now, only support Honolulu (because no new CR in CFU yet)
    new_version_patches = get_new_version_patches(cfu_root, missing_patches)
    results['new_version_patches'] = new_version_patches

    return results


if __name__ == '__main__':
    params = dict(urllib.parse.parse_qsl(sys.argv[1]))

    results = main(params["host_version"], params["installed_updates"])
    print(results)
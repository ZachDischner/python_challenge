#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Zach Dischner'
__copyright__ = ""
__credits__ = ["NA"]
__license__ = "NA"
__version__ = "0.0.0"
__maintainer__ = "Zach Dischner"
__email__ = "zach.dischner@gmail.com"
__status__ = "Dev"
__doc__ = """
File name: ipinfo.py
Created: Mar 30 2017
Modified: Mar 31 2017

Summary:
    Pretty basic, provides some abstract functions for obtaining metadata for IP 
    addresses from various web services
"""

##############################################################################
#                                   Imports
# ----------*----------*----------*----------*----------*----------*----------*
import os
import sys
import requests
from functools import lru_cache
import utils
import argparse
import json

###### Module Wide Objects
_here = os.path.dirname(os.path.realpath(__file__))
logger = utils.logger

_APIs = {"RDAP": "https://rdap.arin.net/bootstrap/ip/{ip}",
         "GEO": "http://freegeoip.net/json/{ip}"}

db = utils.IPDB()

##############################################################################
#                                   Functions
# ----------*----------*----------*----------*----------*----------*----------*

@lru_cache(maxsize=None)
def query_url(ip:str, kind:str) -> dict:
    """Query one of the web REST services for metadata for a given `ip`

    The services' URLs are defined by the module variable _APIs. Results are cached so that, 
    especially in testing, we don't overrun our limited access to web services

    Args:
        ip:     IP address to query against
        kind:   Metadata type identifier. Must be one of the keys defined in `_APIs`
    """
    url = _APIs[kind].format(ip=ip)
    logger.debug(f"Querying {kind} REST service with URL {url}")

    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    logger.warning(f"Error getting {kind} info for ip address: '{ip}'. Reason: '{resp.reason}'")

def fetch_RDAP(ip:str) ->dict:
    """Simple wrapper to fetch RDAP information
    """
    return query_url(ip, "RDAP")

def fetch_GEO(ip:str) -> dict:
     """Simple wrapper to fetch GEO information
     """
     return query_url(ip, "GEO")

def store_info(ip, rdap, geo):
    """Store fetched RDAP and GEO metadata to the `db` interface
    """
    db.update(ip, rdap=rdap, geo=geo)

def ip_lookup(ip, store=False):
    """Higher level function to lookup and store IP metadata from all defined services
    """
    rdap = fetch_RDAP(ip)
    geo = fetch_GEO(ip)
    if store:
        store_info(ip, rdap, geo)
    return rdap, geo

##############################################################################
#                             Runtime Execution
# ----------*----------*----------*----------*----------*----------*----------*
def main(ips=None):
    if ips is None:
        ips = ['244.36.171.60', '244.36.171.61', '192.168.2.11']

    logger.debug("Simple test, fetching metadata for a few IP addresses: {ips}")
    for ip in ips:
        logger.debug("Fetching RDAP metadata for {ip}")
        logger.debug("Fetching RDAP metadata for {ip}")
        print(json.dumps({ip:{"RDAP":fetch_RDAP(ip), "GEO":fetch_GEO(ip)}}, indent=2))
    return 0

if __name__ == '__main__':
    logger.debug("Running main ipinfo.py application")
    parser = argparse.ArgumentParser(description='Fetch metadata for some ip addresses',
        epilog='Example of use: python ipinfo.py 192.168.2.11 192.168.2.12')
    parser.add_argument('ips', metavar='N', type=str, nargs='+',
                    help='IP addresses to query')
    args = parser.parse_args()
    status = main(ips=args.ips)
    sys.exit(status)
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
Created:
Modified:

Summary:
    STATUS IN WORK - Not complete or fully tested yet. 


Details:

Examples:

Nomenclature:

TODO/Improvements:

"""

##############################################################################
#                                   Imports
# ----------*----------*----------*----------*----------*----------*----------*
import os
import sys
import requests
from functools import lru_cache
import utils

###### Module Wide Objects
_here = os.path.dirname(os.path.realpath(__file__))
logger = utils.logger

_APIs = {"RDAP": "https://rdap.arin.net/bootstrap/ip/{ip}",
         "GEO": "http://freegeoip.net/json/{ip}"}

db = utils.ipdb()

##############################################################################
#                                   Functions
# ----------*----------*----------*----------*----------*----------*----------*

@lru_cache(maxsize=None)
def query_url(ip:str, kind:str) -> dict:
    url = _APIs[kind].format(ip=ip)
    logger.debug(f"Querying {kind} REST service with URL {url}")

    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    logger.warning(f"Error getting {kind} info for ip address: '{ip}'. Reason: '{resp.reason}'")

def fetch_RDAP(ip:str) ->dict:
    return query_url(ip, "GEO")

def fetch_GEO(ip:str) -> dict:
    return query_url(ip, "GEO")

def store_info(ip, rdap, geo):
    db.update(ip, rdap=rdap, geo=geo)

def ip_lookup(ip, store=False):
    rdap = fetch_RDAP(ip)
    geo = fetch_GEO(ip)
    if store:
        store_info(ip, rdap, geo)
    return rdap, geo




def main():
    fetch_RDAP('244.36.171.60')
    fetch_GEO('244.36.171.60')
    return 0



##############################################################################
#                             Runtime Execution
# ----------*----------*----------*----------*----------*----------*----------*
if __name__ == '__main__':
    logger.debug("Running main ipinfo.py application")
    status = main()
    sys.exit(status)
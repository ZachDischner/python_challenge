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
File name: ipparser.py
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
import re
import utils

###### Module Wide Objects
_here = os.path.dirname(os.path.realpath(__file__))
logger = utils.logger

# Regex pattern for IP address constraining each section to 0-255
_IP_PATTERN = "\\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b"
_IP_FILE = os.path.join(_here, "list_of_ips.txt")

##############################################################################
#                                   Functions
# ----------*----------*----------*----------*----------*----------*----------*
def ipsearch(searchstring, pattern=_IP_PATTERN):
    """Search a string for an IP address

    Examples:
        >>> ipsearch("foo")
        []
        >>> ipsearch("Praesent in tincidunt 33.33.53.155. In in vehicula 233.151.2.99")
        ['33.33.53.155', '233.151.2.99']
        >>> ipsearch("Okay: 33.33.53.155 . Bad 211.999.191.99")
        ['33.33.53.155']
    """
    matches = [match.group() for match in re.finditer(pattern, searchstring)]
    if matches:
        logger.debug(f"Found {len(matches)} IP addresses in string '{searchstring}'")
    return matches

def extract_ips(fname, pattern=_IP_PATTERN, limit=10):
    extracted = 0
    with open(fname, 'r') as _file:
        for line in _file.readlines():
            matches = ipsearch(line, pattern=pattern)
            for match in matches:
                extracted += 1
                yield match
                if extracted >= limit:
                    logger.debug(f"Maximum parsing limit of {limit} reached.\nStopping parsing of {fname} for IP addresses early")
                    return


def main(ip_filename=_IP_FILE):
    for ip in extract_ips(ip_filename, limit=100):
        print(f"Found IP: {ip}")
    return 0

##############################################################################
#                             Runtime Execution
# ----------*----------*----------*----------*----------*----------*----------*
if __name__ == '__main__':
    logger.debug("Running main ipparser.py application")
    status = main()
    sys.exit(status)
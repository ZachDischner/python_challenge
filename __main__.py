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
File name: utils.py
Created:
Modified:

Summary:
    Main function to parse file of IP addresses, look up GEO/RDAP information, 
    and store in a pickled 'database'


Details:

Examples:

Nomenclature:

TODO/Improvements:

"""

###############################################################################
#                                   Imports
# ----------*----------*----------*----------*----------*----------*----------*
import logging
import os
import sys
import argparse
import ipinfo
import ipparser
import utils

###############################################################################
#                                   Functions
# ----------*----------*----------*----------*----------*----------*----------*
def main(filename, limit, store=True):
    print(f"Parsing IP addresses from {filename}. Storing? {store}. Maximum number of ips limited to {limit}")
    count = 0
    for ip in ipparser.extract_ips(filename, limit=limit):
        _ = ipinfo.ip_lookup(ip, store=store)
        count += 1

    print(f"Finished parsing {count} ips from {filename}")

    if store:
        print("Saving ip database to disk")
        ## Get access to in-memory datastore of IP metadata
        db = utils.IPDB()
        db.commit()
    return 0

if __name__ == "__main__":
    parser   = argparse.ArgumentParser(description='Parse and process IPs from file', 
                    epilog='Example of use: python IPDetective list_of_ips.txt --limit=5 store=True')
    parser.add_argument('filename')
    parser.add_argument('--limit', nargs='?', default=100000, help="Limit to number of IPs parsed from file")
    parser.add_argument('--store', nargs='?', default=True, help="Save results to disk? (JSON file)")
    args = parser.parse_args()
    filename = args.filename
    limit = int(args.limit)
    store = bool(args.store)
    sys.exit(main(filename, limit, store=store))




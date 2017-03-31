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
    Simple module to provide centerpoint definitions for various other modules


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
import pickle
import json
from collections import defaultdict

log_level = logging.DEBUG
logging.basicConfig(stream=sys.stdout, level=log_level)
logger = logging.getLogger("IPDetective")

_here = os.path.dirname(os.path.realpath(__file__))
_DB_LOC = os.path.join(_here, "IPDB.json")  # Location of stored database file
_DB = None # Global database dictionary

###############################################################################
#                                   Functions
# ----------*----------*----------*----------*----------*----------*----------*
def _load_ip_db():
    """Returns faux database of ip information

    'Database' is just a dictionary of the form: {ip_address: {"GEO":geo_json, "RDAP":rdap_json}}. 
    It is stored as a pickle file. If it doesn't exist, an empty dictionary is returned.
    """
    if os.path.exists(_DB_LOC):
        logger.info(f"Loading serialized ip database from {_DB_LOC}")
        with open(_DB_LOC, 'rb') as dbfile:
            # return pickle.load(dbfile)
            return json.load(dbfile)
    else:
        logger.info("No ip 'database' exists. Starting with a clean fresh one")
        return defaultdict(dict)

def get_ip_db(reload=False):
    global _DB
    if reload or _DB is None:
        _DB = _load_ip_db()
    return _DB

def store_ip_db(db):
    logger.info(f"Saving ip database to file {_DB_LOC}. Database has {len(db)} entries in it")
    with open(_DB_LOC, 'w') as dbfile:
        # pickle.dump(db, dbfile)
        json.dump(db, dbfile)


def condition_rdap(rdap, ip):
    """Condition and prepare an RDAP data sample for storage
    
    Doesn't do much for now but keeping as placeholder for good form's sake
    """
    ## Make sure that the RDAP dictionary at least has the `ip` key
    rdap["ip"] = ip

def condition_geo(rdap):
    """Condition and prepare an GEO data sample for storage

    Doesn't do anything for now but keeping as placeholder for good form's sake
    """
    pass

###############################################################################
#                                   Classes
# ----------*----------*----------*----------*----------*----------*----------*
class ipdb(object):
    """Super basic in memory database of ip information.

    ipdb() objects basically wrap access to a dictionary of stored ip:{RDAP, GEO} information.

    The data is all stored in-memory until the `commit()` function is called, at which point
    data is saved to disk. Instantiating this object will either provide reference
    """
    def __init__(self):
        self.db = get_ip_db()

    def update(self, ip, rdap=None, geo=None):
        if rdap is not None:
            logger.debug(f"Updating {ip} RDAP info in database")
            condition_rdap(rdap, ip)
            self.db[ip]["RDAP"] = rdap

        if geo is not None:
            logger.debug(f"Updating {ip} GEO info in database")
            condition_geo(geo)
            self.db[ip]["GEO"] = geo

    def drop(self,ip):
        logger.debug(f"Dropping {ip} info from database")
        self.db.pop(ip)

    def commit(self):
        logger.debug("Storing database information to disk")
        store_ip_db(self.db)
    
    def reload(self):
        self.db = get_ip_db(reload=True)


    
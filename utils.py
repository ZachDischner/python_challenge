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
    Main component here is the `IPDB` class which provides a simplified way to store
    IP address metadata content in an in-memory dictionary and to the disk as a JSON file. 

TODO/Improvements:
    A rework to use the `IPDB` class as a decision point WRT whether or not we need to 
    query the net for metadata would be cool. So far, it is a recieve-only storage interface. 

"""

###############################################################################
#                                   Imports
# ----------*----------*----------*----------*----------*----------*----------*
import logging
import os
import sys
import json
from collections import defaultdict
import numpy as np

log_level = logging.DEBUG
logging.basicConfig(stream=sys.stdout, level=log_level)
logger = logging.getLogger("IPDetective")

_here = os.path.dirname(os.path.realpath(__file__))
_DB_LOC = os.path.join(_here, "IPDB.json")  # Location of stored database file
_DB = None # Global database dictionary

###############################################################################
#                                   Functions
# ----------*----------*----------*----------*----------*----------*----------*
def to_json(data):
    return json.dumps(data, cls=MyEncoder)

def _load_ip_db():
    """Loads a 'database' of stored IP information from a JSON file

    The 'Database' is just a dictionary of the form: {ip_address: {"GEO":geo_json, "RDAP":rdap_json}}. 
    It is stored as a JSON file. If it doesn't exist, an empty dictionary is returned.
    """
    if os.path.exists(_DB_LOC):
        logger.info(f"Loading serialized ip database from {_DB_LOC}")
        try:
            with open(_DB_LOC, 'rb') as dbfile:
                return json.load(dbfile)
        except:
            logger.error(f"Problem loading IP metadata file from disk {_DB_LOC}. Starting with fresh clean metadata database instead")
            return defaultdict(dict)
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
        json.dump(db, dbfile, indent=2)


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
class MyEncoder(json.JSONEncoder):
    """Thank you SO! In Python3/numpy, sometimes numbers are stored as or masquerade as
    simple types when really they are big ones that JSON can't serialize. So here's a nice
    encoder for those cases
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

class IPDB(object):
    """Super basic in memory database of ip information.

    IPDB() objects basically wrap access to a dictionary of stored {ip:{RDAP, GEO}} information.

    The data is all stored in-memory until the `commit()` function is called, at which point
    data is saved to disk to a JSON file.
    """
    ## Class variable which stands as the database accessor (dictionary)
    DB = None

    def __init__(self, reload=False):
        """Instantiate. Access to 'database' is either to the in-memory dictionary or loaded from disk

        Kwargs:
            reload:     Force reload from disk. In-memory DB modifications will be lost!
        """
        if reload or type(self).DB is None:
            type(self).DB = get_ip_db(reload=reload)
        else:
            logger.debug("Database already loaded, using existing reference.")

        # self.db = get_ip_db(reload=reload)
        self.committed = reload
    
    def __repr__(self):
        rep = f"IP info database. Contains {len(IPDB.DB)} entries. "
        if self.committed:
            rep += "All changes are committed to disk"
        else:
            rep += "DB updates have been staged, run 'commit()' to store changes"
        return rep
    
    def update(self, ip, rdap=None, geo=None):
        """Update the database with new RDAP and/or GEO metadata for a given ip ip_address

        Args:
            ip:     String IP address
        
        Kwargs:
            rdap:   Dictionary of RDAP metadata. (hint, fetched from:  "https://rdap.arin.net/bootstrap/ip/{ip}")
            geo:    Dictionary of GEO metadata. (hint, fetched from:  "http://freegeoip.net/json/{ip}")
        
        Examples:
            ipdb.update("192.168.2.11", rdap=requests.get("https://rdap.arin.net/bootstrap/ip/192.168.2.11").json())
        """
            
        if IPDB.DB.get(ip) is None:
            IPDB.DB[ip] = {"GEO":{}, "RDAP":{}}

        if rdap is not None:
            logger.debug(f"Updating {ip} RDAP info in database")
            condition_rdap(rdap, ip)
            IPDB.DB[ip]["RDAP"] = rdap
            self.committed = False

        if geo is not None:
            logger.debug(f"Updating {ip} GEO info in database")
            condition_geo(geo)
            IPDB.DB[ip]["GEO"] = geo
            self.committed = False

    def drop(self,ip):
        """Pops an IP address and associated meta from the database"""
        logger.debug(f"Dropping {ip} info from database")
        IPDB.DB.pop(ip)
        self.committed = False

    def commit(self):
        """Stores in-memory dictionary of metadata to the disk as a JSON file"""
        logger.debug("Storing database information to disk")
        store_ip_db(IPDB.DB)
        self.committed = True


    
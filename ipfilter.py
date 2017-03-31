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
File name: ipfilter.py
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
#----------*----------*----------*----------*----------*----------*----------*
import os
import sys
import utils
import pandas as pd

###### Module Wide Objects
_here = os.path.dirname(os.path.realpath(__file__))
logger = utils.logger


##############################################################################
#                                   Functions
#----------*----------*----------*----------*----------*----------*----------*
def process_datastore(data):
    """Convert a store of ip metadata into a queryable dataframe
    
    Args:
        data:   {dict} Dictionary of data in the format:{ip_address: {"RDAP":rdap_dict, "GEO":geo_dict}, ...}
    """
    geo_data = {ip:data[ip]['GEO'] for ip in data if data[ip].get("GEO")}
    rdap_data = {ip:data[ip]['RDAP'] for ip in data if data[ip].get("RDAP")}

    df_geo = pd.DataFrame([value for value in geo_data.values()])
    df_rdap = pd.DataFrame([value for value in rdap_data.values()])

    ## Sort dataframes by IP because that is nice to have
    df_geo.sort_values(by="ip", inplace=True)
    df_rdap.sort_values(by="ip", inplace=True)

    ## Also, make the IP address the index since we will want to cross reference the two datasets
    df_geo.index = df_geo["ip"]
    df_rdap.index = df_rdap["ip"]

    return df_geo, df_rdap


class IPFilterer(object):
    """
    Queries will be ran against GEO information first, then RDAP info second.
    """
    def __init__(self, data=None, df_geo=None, df_rdap=None):
        """Class to help search/filter out GEO and RDAP IP address information
        
        Must either provide a raw datastore, or specific dataframes filled with
        GEO and RDAP information.
        """
        if data:
            df_geo, df_rdap = process_datastore(data)

        self.df_geo = df_geo
        self.df_rdap = df_rdap

    def filter(self,key,value):
        if isinstance(value, str):
            value = f"'{value}'"

        results_geo = self.df_geo.query(f"""{key}=={value}""")
        if len(results_geo) > 0:
            results_rdap = self.df_rdap.loc[results_geo.index]
        else:
            results_rdap = self.df_rdap.query(f"""{key}=={value}""")
            results_geo = self.df_geo.loc[results_rdap.index]
        return results_geo, results_rdap




###############################################################################
#                             Runtime Execution
#----------*----------*----------*----------*----------*----------*----------*
if __name__ == '__main__':
    logger.debug("Running main ipfilter.py application")
    status = main()
    sys.exit(status)
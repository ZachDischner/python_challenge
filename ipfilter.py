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
    @property
    def content(self):
        return self.to_json()

    def __init__(self, data=None, df_geo=None, df_rdap=None):
        """Class to help search/filter out GEO and RDAP IP address information
        
        Must either provide a raw datastore, or specific dataframes filled with
        GEO and RDAP information.
        """
        if data:
            df_geo, df_rdap = process_datastore(data)
        
        ## Internally stored DataFrames of ip address metadata
        self.df_geo = df_geo
        self.df_rdap = df_rdap

        ## Handy attribute, store searchable keys
        self.searchable = sorted(unique(list(self.df_rdap.keys()) + list(self.df_geo.keys())))
    
    def __repr__(self):
        return f"Filterable IP dataset with {len(self.df_geo)} addresses in it"
    
    def _filter_geo(self,key,value):
        """Base function to get ip addresses that match `key`==`value` condition for GEO metadata

        Returns:
            _:  (list) - List of IP addresses that match that condition 
        """
        return self.df_geo.query(f"""{key}=={value}""")['ip'].values
    
    def ip_subset(self, ips):
        """Take a subset of GEO/RDAP metadata information just for ip addresses `ips`

        As long as at least one address in `ips` exists in the dataframes, subsets will be returned.
        """
        return self.df_geo.loc[ips], self.df_rdap.loc[ips]

    def _filter_rdap(self,key,value):
        return self.df_rdap.query(f"""{key}=={value}""")['ip'].values

    def filter(self,key,value):
        """Filter IP metadata

        Filters according to where `key`==`value`. This method searches through GEO information
        first for a match, then through RDAP information. In either case, whererver the filtering
        conditions are met, the GEO and RDAP information is returned for that subset of IP address.

        Explicitly, filtering is NOT done in place. 

        Returns:
            _:      (IPFilterer()) - A new IPFilterer() object containing just the filtered data subset
        """
        ## First check that the search should even be performed
        if key not in self.searchable:
            logger.warn(f"IP GEO or RDAP metadata store has no attribute '{key}'. Empty store returned")
            logger.debug(f"Attributes you can search through: {self.searchable}")
            return IPFilterer(df_rdap=pd.DataFrame(), df_geo=pd.DataFrame())
        
        ## Condition arguments
        if isinstance(value, str):
            value = f"'{value}'"

        ## Try to filter GEO dataset
        if key in self.df_geo.keys():
            matching_ips = self._filter_geo(key,value)
        else:
            matching_ips = self._filter_rdap(key,value)
        
        df_geo_subset, df_rdap_subset = self.ip_subset(matching_ips)

        return IPFilterer(df_geo=df_geo_subset, df_rdap=df_rdap_subset)
    
    def to_dict(self):
        """Convert (potentially) filtererd IP metadata back into a dictionary that matches JSON data stores
        """
        return {ip:{"RDAP":self.df_rdap.loc[ip].to_dict(), "GEO":self.df_geo.loc[ip].to_dict()} for ip in self.df_geo['ip']}




###############################################################################
#                             Runtime Execution
#----------*----------*----------*----------*----------*----------*----------*
if __name__ == '__main__':
    logger.debug("Running main ipfilter.py application")
    status = main()
    sys.exit(status)
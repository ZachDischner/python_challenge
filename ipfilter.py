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
    Simple module to help you load, filter, and store collections of IP metadata. 

Details:
    IP metadata comes in the form of a dictionary of the structure:
        {ip_address: {"RDAP":rdap_dict, "GEO":geo_dict}, ...}
    This can be a python dictionary, or stored to JSON file. 

    The IPMeta class has methods for filtering down subsets of the loaded metadata and saving
    off new filtered subsets. Under the hood, everything is stored as a pair of GEO/RDAP 
    metadata filled Pandas DataFrames. 

Examples:
    ## Load up metadata
    ipmeta = IPMeta(filename="IPDB.json")
    ipmeta.content                              # Raw dict/JSON metadata representation
    ipmeta.searchable                           # Metadata keys that you can search against

    ## Filter down just USA subsets
    USA_ipmeta = ipmeta.filter_kv("country_name","United States") # Returns another IPMeta() instance
    USA_ipmeta.dump_json("USA_IPs.json")        # Save to file

    ## Back to original dataset, (alphanumerically) filter by a range of IP addresses
    subset = ipmeta.filter_ip_range("192.168.2.11", "195.177.5.11")
    subset.content                              # Raw dict/JSON metadata
    subset.ips                                  # Array of IP addresses associated with this metadata set

    ## Last resort, you can search for any mention of something in metadata. Vague I know
    oddity = ipmeta.filter_mentions('1 Tran Huu Duc')  # Some address component in Vietnam
        # '116.101.14.224' ip address has this address mentioned in the array of `remarks` within RDAP metadata
    # Can be used with numbers
    ones = ipmeta.filter_mentions(1)      # Returns a subset where metadata has a '1' in it, anywhere. 
    my_network = ipmeta.filter_mentions('192.168.2')  # Maybe your network all starts with 192.168


TODO/Improvements:
    * Rework the IPMeta so that it would be able to work with just one metadata type (RDAP/GEO) 
    or both. Best would be if we had an object to do filtering on any 
    type of metadata that it is filled with, then a wrapper that associates filtered info with 
    any other metadata types. Not too clean with repeated GEO/RDAP ops everywhere But oh well.  
    Hindsight and whatnot. 

"""

##############################################################################
#                                   Imports
#----------*----------*----------*----------*----------*----------*----------*
import os
import sys
import utils
import pandas as pd
import json
import argparse

###### Module Wide Objects
_here = os.path.dirname(os.path.realpath(__file__))
logger = utils.logger


##############################################################################
#                                   Functions
#----------*----------*----------*----------*----------*----------*----------*
def load_datastore(filename):
    with open(filename, 'rb') as fp:
        data = json.load(fp)
    return data

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


##############################################################################
#                                 Classes
#----------*----------*----------*----------*----------*----------*----------*
class IPMeta(object):
    """
    Class that contains IP metadata. 
    
    Queries/filtering will be ran against GEO information first, then RDAP info second.
    """
    @property
    def content(self):
        return self.to_dict()
    
    @property
    def ips(self):
        return self.df_geo['ip'].values

    def __init__(self, data=None, filename=None, df_geo=None, df_rdap=None, nanrep=""):
        """Class to help search/filter out GEO and RDAP IP address information
        
        Must either provide a raw metadata dictionary, filename containing stored JSON metadata, 
        or specific dataframes filled with GEO and RDAP information.

        Note: All instantiation options assume matching GEO and RDAP metadata per IP address. Unexpected
        behavior when the two datasets do not have correlated IP addresses can occur. In most cases, it is 
        still workable though.

        Kwargs:
            data:   Dictionary of metadata. See `process_datastore` for description
                                       --or--
            fileanme: Filename full of raw JSON metadata. AKA `data` argument that is stored to  a file
                                       --or--
            df_geo: DataFrame with parsed GEO metadata (One row per IP address GEO metadata)
            df_rdap: DataFrame with parsed RDAP metadata (One row per IP address RDAP metadata)
        """
        if data:
            df_geo, df_rdap = process_datastore(data)
        elif filename:
            df_geo, df_rdap = process_datastore(load_datastore(filename))
        
        ## Internally stored DataFrames of ip address metadata
        self.df_geo = df_geo.fillna(nanrep)
        self.df_rdap = df_rdap.fillna(nanrep)

        ## Handy attribute, store searchable keys
        self.searchable = sorted(pd.np.unique(list(self.df_rdap.keys()) + list(self.df_geo.keys())))
    
    def __repr__(self):
        return f"Filterable IP dataset with {len(self.df_geo)} addresses in it"
    
    def _filter_geo(self,key,value):
        """Base function to get ip addresses that match `key`==`value` condition for GEO metadata

        Returns:
            _:  (list) - List of IP addresses that match that condition 
        """
        return self.df_geo.query(f"""{key}=={value}""")['ip'].values
    
    def _filter_rdap(self,key,value):
        """See _filter_geo()"""
        return self.df_rdap.query(f"""{key}=={value}""")['ip'].values
    
    def ip_subset(self, ips):
        """Take a subset of GEO/RDAP metadata information just for ip addresses `ips`

        As long as at least one address in `ips` exists in the dataframes, subsets will be returned.
        """
        ## Allow for a single IP address
        if isinstance(ips, str):
            ips = [ips]
        return self.df_geo.loc[ips], self.df_rdap.loc[ips]
    
    def filter_ip_list(self, ips):
        """Filter IP datastore by a list of IP addresses

        Example:
            ipmeta.filter_ip_list(['192.168.2.151','192.168.2.155'])
            # Will return an IPMeta instance with GEO/RDAP metadata for IP addresses '192.168.2.151' and '192.168.2.155'
        """
        df_geo, df_rdap = self.ip_subset(ips)
        return IPMeta(df_geo=df_geo, df_rdap=df_rdap)
    
    def filter_ip_range(self, ipmin, ipmax):
        """Filter by IP min and maximum

        **NOTE** IP Range filtering is alphanumeric. So 254.254.254.254 < 5.1.1.1!!

        Example:
            ipmeta.filter_ip_list('192.168.2.151','192.168.2.155')
            # Will return an IPMeta instance with GEO/RDAP metadata for IP addresses '192.168.2.151' through '192.168.2.155'
            # (where metadata exists in the first place, of course)
        """
        df_geo = self.df_geo.query(f"ip > '{ipmin}' and ip < '{ipmax}'")
        df_rdap = self.df_rdap.query(f"ip > '{ipmin}' and ip < '{ipmax}'")
        return IPMeta(df_geo=df_geo, df_rdap=df_rdap)

    def filter_kv(self,key,value):
        """Filter IP metadata by key-value pairs

        Filters according to where `key`==`value`. This method searches through GEO information
        first for a match, then through RDAP information. In either case, whererver the filtering
        conditions are met, the GEO and RDAP information is returned for that subset of IP address.

        Explicitly, filtering is NOT done in place. 

        Returns:
            _:      (IPMeta()) - A new IPMeta() object containing just the filtered data subset
        """
        ## First check that the search should even be performed
        if key not in self.searchable:
            logger.warn(f"IP GEO or RDAP metadata store has no attribute '{key}'. Empty store returned")
            logger.debug(f"Attributes you can search through: {self.searchable}")
            return IPMeta(df_rdap=pd.DataFrame(), df_geo=pd.DataFrame())
        
        ## Condition arguments
        if isinstance(value, str):
            value = f"'{value}'"

        ## Try to filter GEO dataset
        if key in self.df_geo.keys():
            matching_ips = self._filter_geo(key,value)
        else:
            matching_ips = self._filter_rdap(key,value)
        
        df_geo_subset, df_rdap_subset = self.ip_subset(matching_ips)

        return IPMeta(df_geo=df_geo_subset, df_rdap=df_rdap_subset)
    
    def filter_mentions(self, mention):
        """General filter to see if *ANY* of the attributes contain mention of `mention`

        Very non-specific, used pretty much as a last resort. Will be very slow compared to other methods

        Example:
            oddity = ipmeta.filter_mentions('1 Tran Huu Duc')  # Some address component in Vietnam
            # '116.101.14.224' ip address has this address mentioned in one of the `remarks` within RDAP metadata 
        """
        geo_matches = self.df_geo[ self.df_geo.apply(lambda row: True in [str(mention) in str(value) for value in row.iteritems()], axis=1) ]['ip']
        rdap_matches = self.df_rdap[ self.df_rdap.apply(lambda row: True in [str(mention) in str(value) for value in row.iteritems()], axis=1) ]['ip']

        ips = pd.np.unique(list(geo_matches) + list(rdap_matches))

        return self.filter_ip_list(ips)
        # return geo_matches, rdap_matches

    def to_dict(self):
        """Convert (potentially) filtererd IP metadata back into a dictionary that matches JSON data stores
        """
        return {ip:{"RDAP":self.df_rdap.loc[ip].to_dict(), "GEO":self.df_geo.loc[ip].to_dict()} for ip in self.df_geo['ip']}
    
    def dump_json(self, fname):
        """Dump dict/JSON to a file
        """
        with open(fname,'w') as fp:
            json.dump(self.content, fp, indent=2, cls=utils.MyEncoder)
        logger.info(f"Stored filtered IP address metadata to {output}")

##############################################################################
#                             Runtime Execution
#----------*----------*----------*----------*----------*----------*----------*
def main(filename, filter_key, filter_value, output=None):
    logger.info(f"Loading {filename} for filtering where metadata's '{filter_key}' == {filter_value}")
    data = load_datastore(filename)
    
    ipMeta = IPMeta(data=data)

    filtered = ipMeta.filter_kv(filter_key, filter_value)

    logger.info(f"After filtering, metadata went from {len(data)} to {len(filtered.content)} items")

    ###### Store results to file
    if output is None:
        output = filename + ".filtered"
    
    filtered.dump_json(output)

    return filtered


if __name__ == '__main__':
    parser   = argparse.ArgumentParser(description='Filter a file of stored IP GEO/RDAP JSON metadata', 
                    epilog='Example of use: python ipfilter.py IPdata.json "country code" "United States" --output="subset.json"')
    parser.add_argument('input', help="Filename of stored JSON metadata")
    parser.add_argument('filter_key', help="Filtering Key that you are looking for")
    parser.add_argument('filter_value', help="Value that you want filter_key to take on in either RDAP or GEO IP metadata")
    parser.add_argument('--output', nargs='?', default=None, help="Output filename to store filtered IP address metadata to")
    args = parser.parse_args()
    filename = args.input
    output = args.output
    filter_key = args.filter_key
    filter_value = args.filter_value
    status = main(filename, filter_key, filter_value, output=output)
    sys.exit(status)
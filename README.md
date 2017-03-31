# IPDetective 
Zach Dischner - March 31 2017

## Overview
IPDetective is a collection of modules that provides basic utilities for parsing IP addresses from a file, fetching GEO/RDAP metadata for addresses, and filtering down a collection of IPs and associated metadata. The overall approach is as follows:

0. Isolate IP address from file, yield to caller
1. Fetch GEO/RDAP information for that IP address
2. Store to 'database', in this case it is an in-memory dictionary that mirrors a JSON file on disk. 
3. Repeat

**Metadata Model**

```json
{ip1: 
    {"RDAP":rdap_dict,
    "GEO":geo_dict},
...
```

Then, for collections of metadata (in memory dictionary/on-disk JSON), we can filter subsets of IPs/metadata to be re-saved to disk or manipulated in memory. 

### Package Summary
For any python file, call `python thefile.py --help` for usage instructions

* `environment.yml` - Python environment dependancies (notably, Python 3.6, Pandas and Requests)
* `ipparser.py` - Utilities to find IP addresses in a file
* `ipinfo.py` - Utilities to fetch GEO/RDAP metadata information in the form of JSON documents from public APIs for given IP addresses
* `ipfilter.py` - Utilities to load, filter, and store collections of IP address metadata
* `utils.py` - General utilities for logging, accessing and storing fetched IP address metadata. Change log level here for all of `IPDetective` logging. 
* `__main__.py` - Makes package callable, parses file of ip addresses and stores to JSON file on disk

## Basic Examples:
**Parse file for IPs, find and store metadata to JSON file. Limit total number parsed to 10 for convenience**
Note: Any calls to this will store metadata to `IPDB.json`. 

```bash
python IPDetective IPDetective/list_of_ips.txt --limit=10
# Equivalent:
python IPDetective/__main__.py IPDetective/list_of_ips.txt --limit=10
```

**Parse 20 IPs from a file. Printout**

```bash
python IPDetective/ipparser.py IPDetective/list_of_ips.txt --limit=10
```

**Lookup GEO/RDAP metadata for a few IP addresses**

Hint: If you turn logging way up (in `utils.py`) the only output will be metadata collections which you can pipe directly to a JSON file!

```bash
python IPDetective/ipinfo.py 192.168.2.11 192.168.2.12
```

**Basic Key-Value Filtering of Metadata**
Filter out only IP addresses whose associated metadata contains the `country_code`: `'United States'`, save subset to a new JSON file called `subset.json`

```bash
python ipfilter.py IPDB.json "country_code" "United States" --output="subset.json"
```

## Filtering
Arguably the most complex part of this is filtering of fetched and stored metadata. See `ipfilter.py` for more information, some illustrative examples of how you can filter metadata is given below. You can basically perform 4 different filtrering actions:

* Filter where you want either GEO/RDAP metadata's `key` to be equal to a `value`
* Filter by a given set of ip addresses
* Filter by an alphanumeric range of ip addresses
* Filter very generally where you just want the metadata somewhere to contain a `mention` of something

In any case, you start with a collection of metadata loaded into an `IPMeta` class. Further filterings will return new instances of the same `IPMeta` class. That class has ways to self-convert to JSON files, or a raw dictionary of metadata. Under the hood, metadata is converted to Pandas DataFrames for sorting/searching. Neat! 

```python
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
```



## Problem Statement as Given

**Requirements:**
> Create a program that will read a given set of IPs, perform Geo IP and RDAP lookups, and accept a query to filter results.

**Objectives:**
>   This exercise is designed to test your ability to:
    Take abstract requirements and run with them
    Write isolated decoupled modules with strict input/output interfaces
    Create a query language and algorithm for filtering
    Reading, parsing, and extracting IP addresses from unstructured text in an efficient manner
    Once you are done, please post your code on Github named something like: https://github.com/*profileID*/python_challenge

**Technical:**
>    Each component (GeoIP/RDAP/Filter/Parsing) should be as decoupled from the others as possible while still being easy to use.
    The main function should parse a text file containing 5000 IP addresses spread throughout random text.
    The filter component should provide a custom query language allowing the user to easily filter results based on
    Do not use 3rd party packages that provide complete solutions for GeoIP queries, RDAP queries, or filtering. Libraries simplifying HTTP requests, data manipulation, etc. are acceptable.
    Bonus points for simple, clever, and performant solutions, and any extras like unit tests, docs, multiple output formats, result caching, web UI, cli, etc. Be creative.
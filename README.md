# IPDetective 
Zach Dischner - March 31 2017

Clone with `git clone git@github.com:ZachDischner/swimlane_challenge.git IPDetective`

Make sure your environment is up-to-snuff as described by `environment.yaml`

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
    
**File structure**

5000 IP addresses interspersed in a text file like:

```
Lorem ipsum dolor sit amet, 244.36.171.60 adipiscing elit. Pellentesque finibus massa vitae augue 81.44.150.240, vitae faucibus quam pellentesque. Aenean condimentum risus at justo suscipit bibendum. Curabitur consequat tempus bibendum. Vestibulum bibendum sagittis odio, in fermentum velit auctor eget. Etiam mollis aliquet semper. Sed id turpis ac nulla congue rhoncus. 40.82.106.5 facilisis sem augue, sit amet consequat lacus pellentesque sed. Fusce non posuere ligula. Praesent nec lorem nisl. Integer suscipit efficitur nibh consectetur malesuada.

Aliquam porta ullamcorper lorem, non 216.235.211.155 erat scelerisque eget. 116.101.14.224 finibus eu leo vitae 34.142.6.33. Fusce eu arcu eu metus dignissim hendrerit a in eros. Aenean elementum, mi id interdum hendrerit, odio erat dapibus nisl, sit amet feugiat purus massa ut eros. Duis lacus velit, facilisis ut dignissim vel, tempus id turpis. Vivamus laoreet sollicitudin metus vitae consequat. Praesent sapien massa, fringilla tempus finibus et, dapibus sit amet risus. Fusce in rhoncus tellus.

Praesent in tincidunt 33.33.53.155. In in vehicula est, nec finibus urna. Nulla 186.167.42.67 arcu, bibendum quis erat in, viverra sodales erat. Vestibulum non scelerisque nibh, a viverra quam. Proin vitae odio ac leo dignissim mollis auctor ac libero. Cras sollicitudin lobortis risus eget aliquet. Morbi mattis id felis sed molestie. Praesent semper tellus a est ornare vulputate. Suspendisse rhoncus neque purus, non ornare sem pellentesque maximus.

236.220.190.72
208.128.240.230
123.42.170.221

224.171.234.30
3.173.155.119
40.43.195.14
232.125.33.216

31.57.136.230
222.5.172.196
33.238.19.104
142.254.194.243
124.86.226.223

Etiam quis 13.211.237.22 eros. Donec massa nunc, 4.44.97.176 vel ligula ut, dapibus 203.35.56.248 eros. Pellentesque malesuada nisi 24.197.112.182, a malesuada mi feugiat vitae. Nulla vitae ante at odio imperdiet varius 107.73.246.73 in justo. Sed nisi leo, venenatis vitae lorem et, porta eleifend arcu. Fusce ornare tempor lacinia. Vestibulum at diam eu libero lobortis pulvinar a non ex. 108.65.14.158 a neque ullamcorper, lacinia odio in, mattis est. Integer rhoncus neque sit amet lorem pulvinar, at pretium libero venenatis. Aenean tristique semper hendrerit. Praesent molestie mauris sed justo bibendum facilisis. Proin lorem magna, rutrum vel finibus eget, eleifend vel dui. 72.240.178.112 Donec fringilla nisi et erat iaculis rhoncus sed a nibh. Mauris semper 59.219.223.23 vel interdum vulputate. Mauris ut rhoncus nunc. Cras nec lectus eget lectus pretium tincidunt. Pellentesque magna ex, maximus sed imperdiet nec, molestie in sem. Ut efficitur 61.66.194.204 et porta mollis. Donec eu ex in purus tincidunt suscipit. 159.129.75.124 interdum velit velit, quis aliquam ante malesuada aliquet. Nunc ante enim, lobortis nec aliquet nec, vulputate vitae 227.73.226.94. Vivamus dapibus imperdiet augue, nec sagittis tellus lobortis vitae. Quisque ligula elit, 99.174.36.137 vitae justo vitae, porttitor malesuada 23.5.102.194.

41.107.216.31
136.17.123.206
54.153.173.116
184.159.117.150
221.88.104.235
14.187.35.51
...
```
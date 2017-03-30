## Challenge as given 

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
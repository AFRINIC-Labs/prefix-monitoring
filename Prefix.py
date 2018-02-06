#!/usr/bin/env python

import csv
from netaddr import *
import urllib, json
import os, glob
from collections import defaultdict
import multiprocessing

BGP_LOOKING_GLASS_URL="https://stat.ripe.net/data/looking-glass/data.json?resource="
URL_IRREXPLORER = "http://irrexplorer.nlnog.net/json/prefix/"
IPSETS_PATH = "data/ipsets/subset/"
IPRESOURCES_PATH = "ftp://ftp.afrinic.net/stats/afrinic/delegated-afrinic-extended-latest"

#get the number of objects found in the IRR databases
def findIRRObjects(prefix):
    url = URL_IRREXPLORER + prefix
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return len(data)

def findBLIPs(filename):
    with open(filename) as fp:
        for line in fp:
            if line.startswith("#"):
                continue
            ipn = IPNetwork(line)
            s = IPSet(ipn)
            if afrinicPrefixes.intersection(s):
                print (ipn, filename)

def loadAFRINICPrefixes(filepath):
    ranges = IPSet()
    with open(filepath) as csvfile:
        reader = csv.reader(csvfile, delimiter='|')
        for p in reader:
            prefix = p[3]
            prefixlength = p[4]
            startip = IPAddress(prefix)
            endipint = int(startip) + int(prefixlength) -1
            endip = IPAddress(endipint)
            range = IPRange(startip, endip)
            ranges.add(range.cidrs()[0])
    return ranges


#load AFRINIC prefixes
afrinicPrefixes = loadAFRINICPrefixes('data/ipv4.txt')


p = multiprocessing.Pool()
jobs = []

for f in glob.glob(IPSETS_PATH+"*.*set"):
    # launch a process for each file (ish).
    # The result will be approximately one process per CPU core available.
    jobs.append(p.apply_async(findBLIPs, [f]))


#wait for all jobs to finish
for job in jobs:
    job.get()

p.close()
#p.join() # Wait for all child processes to close.
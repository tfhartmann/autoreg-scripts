#!/usr/bin/python
# name:    update-lastseen.py
# version: .01
# author:  Tim Hartmann
# summary: Poll netmri for last seen data
# description "Poll NetMRI for Last Seen data and format it in such a way that it's useful to autoreg"

import urllib
import urllib2
import cookielib
import json
import socket
import argparse
import os
import sys
import re

# Unset https_proxy env var
del os.environ['https_proxy']

parser = argparse.ArgumentParser(description='Update Last Seen Data from NetMRI API',
    epilog='Example: update-lastseen.py --debug')
       
parser.add_argument('--debug', dest='DEBUG', action='store_true',
    help='Echo debug output to stdout')

parser.add_argument('-H', '--host', dest='mri_url', action='store',
    required='True', metavar='https://netmri.example.com',
    help='Base URL for NetMRI')

parser.add_argument('-u', '--user', dest='mri_user', action='store',
    required='True', metavar='username',
    help='username that has API access')

parser.add_argument('-p', '--password', dest='mri_password', action='store',
    required='True', metavar='Password1234',
    help='username that has API access')
       
args = parser.parse_args()



# NetMRI Configs
mri_ver    = '/api/2.6'
#mri_qry    = mri_ver+'/devices/index.json?limit=5000'
mri_qry    = mri_ver+'/spm_end_hosts_default_grids/index.json?limit=50000'
mri_url    = args.mri_url
mri_user   = args.mri_user
mri_passwd = args.mri_password

def discoverNetMRI (base_url, query, user, passwd):
    # discoverNetMRI returns a dict
    authurl  = base_url+'/api/authenticate.json?username='+user+'&'+'password='+passwd
    COOKIEFILE = '/tmp/cookies.lwp'
    urlopen = urllib2.urlopen
    Request = urllib2.Request
    txdata = None
    cj = cookielib.LWPCookieJar()
   
    if cj is not None:
        if os.path.isfile(COOKIEFILE):
            cj.load(COOKIEFILE)
       
        if cookielib is not None:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
        else:
            opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
            ClientCookie.install_opener(opener)
    try:
        req = Request(authurl, txdata)
        # create a request object
        handle = urlopen(req)
        # and open it to return a handle on the url
   
    except IOError, e:
        print 'We failed to open "%s".' % authurl
        if hasattr(e, 'code'):
            print 'We failed with error code - %s.' % e.code
        elif hasattr(e, 'reason'):
            print "The error object has the following 'reason' attribute :"
            print e.reason
        sys.exit()
   
    # save the cookies again
    cj.save(COOKIEFILE)
   
    try:
        raw_data = urllib2.urlopen(base_url + query)
        for line in raw_data:
            data = json.loads(line)
        return data
    except IOError, e:
        print 'We failed to open "%s".' % authurl
        if hasattr(e, 'code'):
            print 'We failed with error code - %s.' % e.code
        elif hasattr(e, 'reason'):
            print "The error object has the following 'reason' attribute :"
            print e.reason
            print 'This usually means the server doesn\'t exist,',
            print 'is down, or we don\'t have an internet connection.'
        sys.exit()
# End discoverNetMRI

def devicesNetMRI ( data ):
    # take data from NetMRI's /api/2.4/devices API and cook it
    database = {}
    for k, v in data.iteritems():
        if k == 'spm_end_hosts_default_grids':
            for item in v:
                key = item['NeighborMAC'].split('.')
                database.update({key[0]: item})
    return database
# End devicesNetMRI



raw = discoverNetMRI(mri_url, mri_qry, mri_user, mri_passwd )
devices = devicesNetMRI (raw) 

header1 = "mac_lan\tmac_host\tmac_address\tmac_port\tip_address\tip_host\tip_int\tage"
header2 = "vlan\thost\t\tmac\t\tport\t0.0.0.0\tDNE\tDNE\tDNE"

print header1
print header2
#print devices


# Debug output for Testing
for k,v in devices.iteritems():
    lastseen = {}
    if args.DEBUG == True:
        print '########'
        print k
    print [v].items()
   
    if args.DEBUG == True:
        for a, b in devices[k].iteritems():
            print a, b
        print '########'


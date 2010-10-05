#!/usr/bin/python
#
# (P) Sergiusz Pawlowicz 2008
# (C) GPLv3
# http://code.google.com/p/ecostats/
#

#import cgi
#cgi.test()
#
# URI translator 
# used for flexible change of graph rendering helper

import os

# always print headers ;-)
#print "Content-type: image/png"
print "Content-type: text/html"
print

# then simple forward QUERY_STRING to proper script and include it on the helper page
try:
        query = os.environ['QUERY_STRING']
except:
        query = "hostname=beton;plugin=load;type=load;begin=-3600"

print '<img src="/static/c/graph.cgi?%s">' % query

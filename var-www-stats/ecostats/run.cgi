#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (P) Sergiusz Pawlowicz 2008
# (C) GPLv3
# http://code.google.com/p/ecostats/
#
#
print "Content-Type: text/html; charset=utf-8"
print ""

#
import os, rrdtool, operator, re, sys
rrdbase = "/var/lib/collectd/db/"
uri = "#"
alphabet = 'abcdefghkmnopqrstuvwxyz'

# an idea to switch between len and number
def tonumber(value,lenght):
	return str(value/(10**(lenght-1)))

# an idea to get an average
def average(seq):
        return reduce(operator.add,seq)/len(seq)

# set color of cell
def setstate(datas, level):
	try:
		value = int(datas*10)
		lenght = len(str(value))
		position = 1
		state ='class="state%s%s"' \
			% (alphabet[lenght] , tonumber(value,lenght) )
	except:
	       	state = 'class="statez"'
       	return state

# get average value from all known values different then None
def getaverage ( host , process , uri , time, value ):
        '''
        uri = uri of related graphing script
        period = period for we counting average
        '''
	if process == 'load':
		info = rrdtool.fetch(rrdbase+host+"/load/load.rrd", "AVERAGE", "%s" % time ) 
	elif process == 'eth0':
		info = rrdtool.fetch(rrdbase+host+"/interface/if_octets-eth0.rrd", "AVERAGE", "%s" % time )
	elif process == 'eth1':
		info = rrdtool.fetch(rrdbase+host+"/interface/if_octets-eth1.rrd", "AVERAGE", "%s" % time )
	elif process == 'disk_octets-sda':
		info = rrdtool.fetch(rrdbase+host+"/disk-sda/disk_octets.rrd", "AVERAGE", "%s" % time )
	elif process == 'disk_octets-sdb':
		info = rrdtool.fetch(rrdbase+host+"/disk-sdb/disk_octets.rrd", "AVERAGE", "%s" % time )
	elif process == 'disk_octets-sdc':
		info = rrdtool.fetch(rrdbase+host+"/disk-sdc/disk_octets.rrd", "AVERAGE", "%s" % time )
	elif process == 'disk_octets-sdd':
		info = rrdtool.fetch(rrdbase+host+"/disk-sdd/disk_octets.rrd", "AVERAGE", "%s" % time )
	elif process == 'apache_requests':
		info = rrdtool.fetch(rrdbase+host+"/apache/apache_requests.rrd", "AVERAGE", "%s" % time )
	elif process == 'apache_bytes':
		info = rrdtool.fetch(rrdbase+host+"/apache/apache_bytes.rrd", "AVERAGE", "%s" % time )
	elif process == 'mysql_octets':
		info = rrdtool.fetch(rrdbase+host+"/mysql/mysql_octets.rrd", "AVERAGE", "%s" % time )
	values = []
	for x in info:
		for y in x:
			# try the easiest average, as it is informative, i do not care
			try: 
				values.append(float(y[value])) 
			except:
				pass
	
	datas = float(average(values))
	
	#state = setstate(datas, 100)
	#print datas

	return datas

allhosts = os.listdir(rrdbase)
print "<table>"
print "<tr>"
print "<td class='livehead'>SERVER</td>"
print "<td class='livehead'>load</td>"
print "<td class='livehead'>eth0<br>kbit/s</td>"
print "<td class='livehead'>eth1<br>kbit/s</td>"
print "<td class='livehead'>sda<br>kbit/s</td>"
print "<td class='livehead'>sdb<br>kbit/s</td>"
print "<td class='livehead'>sdc<br>kbit/s</td>"
print "<td class='livehead'>sdd<br>kbit/s</td>"
#print "<td class='head'>apache<br>req/s</td>"
#print "<td class='head'>apache<br>kbit/s</td>"
print "<td class='livehead'>mysql<br>kbit/s</td>"
print "</tr>"
# grapwidth
graphwidth="920"
for host in sorted(allhosts):
#for host in ['nolapp111']:
	# get hostname without domain
	dot = re.compile(r'\.')
	hostname = dot.split(host)[0]
	print "<tr><td class='livehead'>%s</td>" % hostname
	# for each selected plugin do
	#for process in ['load', 'eth0', 'eth1', 'disk_octets', 'apache_requests', 'apache_bytes']:
	for process in ['load', 'eth0', 'eth1', 'disk_octets', 'mysql_octets']:
	#for process in ['load', 'eth0', 'eth1', 'disk_octets']:
#		try:
		if "a" == "a":
		 if process == 'load':
			print "<td>"
			try:
			 for inout in [0,2]:
			  try:
				# ('shortterm', 'midterm', 'longterm')
				data = getaverage ( host, process, uri, "-s now-1h", inout )
				if inout == 0: graphtime = "5000"
                                else: graphtime = "100000"
				uri = "/ecostats/i.cgi?hostname=%s;plugin=load;type=load;begin=-%s&width=%s" % ( host, graphtime, graphwidth )
				print "<p %s>" % setstate(float(data*100),1)
				#print '<a href="%s" id="%s" rel="%s" class="jTip">' % (uri,process,uri)
				#print '<a href="%s" rel="%s" class="jTip">' % (uri,uri)
				print '<a href="%s" id="%s" name="%s" class="jTip">' % (uri,host,host)
				print "%5.2f</a></p>" % data
			  except: print "<p class='livehead'>&nbsp;</p>"
			except: print "<p class='livehead'>&nbsp;</p>"
			print "</td>"
		 elif process == 'eth0' or process == 'eth1':
			# ('rx', 'tx')
#			print "<table>"
			print "<td>"
			try:
			 for inout in [0,1]:
			  try:
				 graphtime = "-s now-1h"
				 data = getaverage ( host, process, uri, graphtime, inout )
				 if inout == 0: graphtime = "5000"
				 else: graphtime = "100000"
 				 uri = "/ecostats/i.cgi?hostname=%s;plugin=interface;type=if_octets;type_instance=%s;begin=-%s&width=%s" % (host, process, graphtime, graphwidth)
				 #print "<p %s>" % setstate(float(data/100),100)
				 print "<p %s>" % setstate(float(data/100),1)
				 if inout == 0: print "&#187;"
				 else: print "&#171;"
				 print '<a href="%s" class="jTip"' % uri
				 print ' id="%s" name="%s" width="500">' % (hostname,hostname)
				 print "%5.2f</a></p>" % float(data/100)
			  except: print "<p class='livehead'>-</p>"
			except: print "<p class='livehead'>-</p>"
			print "</td>"
			#print str(data)
		 elif process == 'disk_octets':
			try:
			 for drive in ['sda','sdb','sdc','sdd']:
			# ('read', 'write')
			  print "<td>"
			  try:
			   for inout in [1,0]:
				try:
				 data = getaverage ( host, process+"-"+drive, uri, "-s now-1h", inout )
				 if inout == 1: graphtime = "5000"
				 else: graphtime = "100000"
				 uri = "/ecostats/i.cgi?hostname=%s;plugin=disk;plugin_instance=%s;type=disk_octets;begin=-%s&width=%s" % (host,drive, graphtime, graphwidth )
				 print "<p %s>" % setstate(float(data/100),100)
				 if inout == 1: print "&#187;"
				 else: print "&#171;"
				 print '<a href="%s" class="jTip"' % uri
				 print ' id="%s" name="%s" width="500">' % (hostname,hostname)
				 print "%5.2f</a></p>" % float(8*(data/1000)) # we want kbit/s
				except: print "<p class='livehead'>-</p>"
			  except: print "<p class='livehead'>-</p>"
			  print "</td>"
			except: print "<td class='livehead'>-</td>"

		 # mysql
		 elif process == 'mysql_octets':
			print "<td>"
			try:
			 for inout in [0,1]:
			  try:
				# ('tx', 'rx')
				data = getaverage ( host, process, uri, "-s now-1h", inout )
				if inout == 0: graphtime = "5000"
                                else: graphtime = "100000"
				uri = "/ecostats/i.cgi?hostname=%s;plugin=mysql;type=mysql_octets;begin=-%s&width=%s" % ( host, graphtime, graphwidth )
				print "<p %s>" % setstate(float(data/100),100)
				if inout == 0: print "&#187;"
				else: print "&#171;"
				print '<a href="%s" id="%s" name="%s" class="jTip">' % (uri,host,host)
				print "%5.2f</a></p>" % float(8*(data/1000)) # we want kbit/s
			  except: print "<p class='livehead'>-</p>"
			except: print "<p class='livehead'>-</p>"
			print "</td>"

		 elif process == 'apache_requests':
			try:
				data = getaverage ( host, process, uri, "-s now-1h", 0 )
				print "<td %s>%5.2f</td>" % (setstate(data,100), data)
			except:	print "<td class='livehead'>&nbsp;</td>"
		 elif process == 'apache_bytes':
			try:
				data = getaverage ( host, process, uri, "-s now-1h", 0 )
				print "<td %s>%5.2f</td>" % (setstate(float(data/100),100), float(data/100))
			except:	print "<td class='livehead'>&nbsp;</td>"
#		except:
#			print "<td class='livehead'>+</td>"
	print "</tr>"
	#sys.exit()
print "</table>"

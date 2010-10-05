#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (P) Sergiusz Pawlowicz 2008
# (C) GPLv3
# http://code.google.com/p/ecostats/
#
# Rewrote by Carlos Lopez <clopez@igalia.com>


import os, rrdtool, operator, re, sys
rrdbase = "/var/lib/collectd/rrd/"
uri = "#"
alphabet = 'abcdefghkmnopqrstuvwxyz'
nfile = "/tmp/.collectdnotifications"

# Code for flush borrowed from :
# /usr/share/doc/collectd-core/examples/collectd_unixsock.py
#
class collectdsocket():

    # Check the path to your socket file
    def __init__(self, path='/var/run/collectd-unixsocket'):
        import socket
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.connect(path)

    def __del__(self):
        self._sock.close()

    def flush(self, timeout=None, plugins=[], identifiers=[]):
        """
        Send a FLUSH command.

        Full documentation:
            http://collectd.org/wiki/index.php/Plain_text_protocol#FLUSH

        """
        # have to pass at least one plugin or identifier
        if not plugins and not identifiers:
            return None

        args = []
        if timeout:
            args.append("timeout=%s" % timeout)
        if plugins:
            plugin_args = map(lambda x: "plugin=%s" % x, plugins)
            args.extend(plugin_args)
        if identifiers:
            identifier_args = map(lambda x: "identifier=%s" % x, identifiers)
            args.extend(identifier_args)

        self._sock.send('FLUSH %s' % ' '.join(args) + "\n")

        #Read single line from socket
        data = ''
        buf = []
        recv = self._sock.recv
        while data != "\n":
            data = recv(1)
            if not data:
                break
            if data != "\n":
                buf.append(data)
        status_message = ''.join(buf)
        code, message = status_message.split(' ', 1)

        if int(code) == 0:
            return True
        return False






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
def getaverage ( host , process , instance, value ):

    if   process == 'load':                 file = "load.rrd"
    elif process == 'interface':            file = "if_octets-eth0.rrd"
    elif process == 'disk_octets-sda1':     file = "disk_octets.rrd"
    elif process == 'apache_requests':      file = "apache_requests.rrd"
    elif process == 'apache_bytes':         file = "apache_bytes.rrd"
    elif process == 'nginx':                file = "nginx_requests.rrd"
    else:                                   return # Not supported


    time = "-s now-1h"
    identifier = host + "/" + process + "/" + instance

    # Try to flush the values
    try:
        cflush = collectdsocket()
        cflush.flush(None, [], identifier)
    except:
        pass


    info = rrdtool.fetch(os.path.join(rrdbase,host,instance,file), "AVERAGE", "%s" % time )
    values = []
    for x in info:
        for y in x:
            # try the easiest average, as it is informative, i do not care
            try:
                values.append(float(y[value]))
            except:
                pass

    datas = float(average(values))

    return datas

# Saves the status of host in a dictionary and writes it to disk
def writevalue(host, status):
    # Lazy import
    import pickle

    # Load from disk if we can
    if os.path.isfile(nfile):
        ndict = pickle.load( open( nfile ) )
    else:
        ndict = {}

    if status.strip() == 'OKAY':
        ndict[host] = True
    else:
        ndict[host] = False
    # Save it
    pickle.dump( ndict, open( nfile, "w" ) )
    # And make it readable by any user. Later we will be called as www-data
    os.chmod(nfile,0644)

# Read the status of a host from the dictionary. Loads it from disk
def isok(host):
    # Lazy import
    import pickle

    # If there is no file with data means that no alert was processed
    if not os.path.isfile(nfile):
        return True
    # Load the data
    ndict = pickle.load( open( nfile ) )

    if host in ndict:
        return ndict[host]

    # If host wasn't in dict no alert for this host was processed
    return True


def rendertable():

    print "Content-Type: text/html; charset=utf-8"
    print ""

    allhosts = os.listdir(rrdbase)
    print "<table>"
    print "<tr>"
    print "<td class='livehead'>SERVER</td>"
    print "<td class='livehead'>load</td>"
    print "<td class='livehead'>disk<br>kB/s</td>"
    print "<td class='livehead'>network<br>kB/s</td>"
    print "<td class='livehead'>apache<br>request/s</td>"
    print "<td class='livehead'>apache<br>kB/s</td>"
    print "<td class='livehead'>nginx<br>request/s</td>"
    print "<td class='livehead'>STATUS</td>"
    print "</tr>"

    graphwidth="740"
    graphtime="3600"
    for host in sorted(allhosts):
        dot = re.compile(r'\.')
        hostname = dot.split(host)[0]


        print "<tr><td class='livehead'>%s</td>" % hostname
        # for each selected plugin do

        for process in ['load', 'disk_octets', 'interface', 'apache_requests', 'apache_bytes', 'nginx','status']:

            if process == 'load':
                print "<td>"
                try:
                    data = getaverage ( host, process, process, 0 )
                    uri = "/stats/ecostats/i.cgi?hostname=%s;plugin=load;type=load;begin=-%s&width=%s" % ( host, graphtime, graphwidth )
                    print "<p %s>" % setstate(float(data*100),1)
                    print '<a href="%s" id="%s" name="%s" class="jTip" >' % (uri,host,host)
                    print "%5.2f</a></p>" % data
                except:
                    print "<p class='livehead'>&nbsp;</p>"
                print "</td>"

            elif process == 'interface':
                # ('rx', 'tx')
                print "<td>"
                try:
                    for inout in [0,1]:
                        try:

                            data = getaverage ( host, process, process, inout )
                            uri = "/stats/ecostats/i.cgi?hostname=%s;plugin=%s;type=if_octets;type_instance=eth0;begin=-%s&width=%s" % (host, process, graphtime, graphwidth)
                            print "<p %s>" % setstate(float(data/100),1)
                            if inout == 0: print "&#187;"
                            else: print "&#171;"
                            print '<a href="%s" class="jTip"' % uri
                            print ' id="%s" name="%s" width="500">' % (hostname,hostname)
                            print "%5.2f</a></p>" % float(data/(8*1024))  # we want kbytes/s
                        except:
                            print "<p class='livehead'>-</p>"
                except:
                    print "<p class='livehead'>-</p>"
                print "</td>"

            elif process == 'disk_octets':
                drive="sda1"
                print "<td>"
                for inout in [1,0]:
                    try:
                        data = getaverage ( host, process+"-"+drive, "disk"+"-"+drive, inout )
                        uri = "/stats/ecostats/i.cgi?hostname=%s;plugin=disk;plugin_instance=%s;type=disk_octets;begin=-%s&width=%s" % (host,drive, graphtime, graphwidth )
                        print "<p %s>" % setstate(float(data/100),100)
                        if inout == 1: print "&#187;"
                        else: print "&#171;"
                        print '<a href="%s" class="jTip"' % uri
                        print ' id="%s" name="%s" width="500">' % (hostname,hostname)
                        print "%5.2f</a></p>" % float(data/1024) # we want kbytes/s
                    except:
                        print "<p class='livehead'>-</p>"
                print "</td>"

            elif process == 'apache_requests' or process == 'apache_bytes':
                print "<td>"
                # Search for the name of the entry ID
                entry = None
                for direntry in os.listdir(rrdbase+host):
                    if os.path.isdir(os.path.join(rrdbase,host,direntry)) and direntry.startswith("apache-"):
                        entry=direntry
                        break
                if entry:
                    (apachehost,apacheinstance) = entry.split("-", 1)
                    try:
                        data = getaverage ( host, process, entry, 0 )
                        uri = "/stats/ecostats/i.cgi?hostname=%s;plugin=apache;plugin_instance=%s;type=%s;begin=-%s&width=%s" % (host,apacheinstance,process, graphtime, graphwidth )

                        print '<a href="%s" id="%s" name="%s" class="jTip">' % (uri,host,host)
                        if process == 'apache_bytes':
                            print "<p %s>" % setstate(float(data/100),1)
                            print "%5.2f</a></p>" %float(data/(8*1024)) #kbytes/sec
                        else:
                            print "<p %s>" % setstate(float(data*100),1)
                            print "%5.2f</a></p>" %data
                    except:
                        print "<p class='livehead'>&nbsp;</p>"
                print "</td>"

            elif process == 'nginx':
                print "<td>"
                try:
                    data = getaverage ( host, process, process, 0 )
                    uri = "/stats/ecostats/i.cgi?hostname=%s;plugin=nginx;type=nginx_requests;begin=-%s&width=%s" % ( host, graphtime, graphwidth )
                    print "<p %s>" % setstate(float(data*100),1)
                    print '<a href="%s" id="%s" name="%s" class="jTip">' % (uri,host,host)
                    print "%5.2f</a></p>" % data
                except:
                    print "<p class='livehead'>&nbsp;</p>"
                print "</td>"

            elif process == 'status':
                print "<td>"
                try:
                    if isok(host):
                        print "<p class='greenok'>OK</p>"
                    else:
                        print "<p class='redalert'>FAILURE</p>"
                except:
                    print "<p class='livehead'>UNKNOW</p>"
                print "</td>"



        print "</tr>"

    print "</table>"



if __name__ == '__main__':

    # if We are called with -pipe read from stdin
    # This is used to parse alert emails with postfix
    if len(sys.argv) == 2 and sys.argv[1] == '-pipe' :
        try:
            import re
            lines = sys.stdin.readlines()
            if lines:
                for line in lines:
                    if re.match('^Subject: Collectd notify:', line) != None:
                        line = re.sub('^Subject: Collectd notify:','',line).strip()
                        (status,host) = line.split('@',1)
                        # Save the data to disk
                        writevalue(host,status)
        except:
            # Something wrong happened. But:
            # We don't want procmail to think that the mail was not delivered
            pass

    else:
         rendertable()



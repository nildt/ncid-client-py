#!/usr/bin/python -u
# -*- coding: utf-8 -*-


# Uses the daemon implementation from http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/ 


'''simple tcp client'''

# notification in Ubuntu
import pynotify 
import gtk.gdk

# I should daemonize it... Want it in Background
from daemon import daemon
import sys
import os

# apt-get install python-configobj
from configobj import ConfigObj

# apt-get install python-twisted
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from datetime import datetime

# Read config file 
CONFIG = ConfigObj('./ncid-client.cfg')
# Reads config and gives an exemple
SERVER_IP = CONFIG.get('server_ip', '192.168.2.1')
SERVER_PORT = int(CONFIG.get('server_port', 3333))

# Prints Notifications
class Notify(object):
	def showNotification(self,notification,zeit):
#		import time
		pynotify.init("CallAlertWindow")
		msg = pynotify.Notification("CallAlert", notification, "notification-message-im")
		msg.set_urgency(pynotify.URGENCY_CRITICAL)
		msg.set_hint('x', gtk.gdk.screen_width()/2.)
		msg.set_hint('y', gtk.gdk.screen_height()/2.)
		msg.set_timeout(zeit)
		msg.show()

''' Tried to workaround the close problem... '''
#		time.sleep(1)
#		msg.update(" "," "," ")
#		msg.show()
#		time.sleep(2)
#		msg.clsose() 

class NcidClient(LineReceiver):
	def lineReceived(self, line):
		if line.startswith('200 NCID Server:  ARC_ncidd 0.01'):
			print "Date:	   ","Time: ","Number:"
		elif line.startswith('CIDLOG:'):
			data = line.split('*')
			date, time, phonenr = data[2], data[4], data[8]
			tstamp_log = datetime.strptime('%s %s' % (date, time), '%d%m%Y %H%M').strftime('%Y-%m-%d %H:%M')
			print ('%s %s' % (str(tstamp_log), phonenr))
		elif line.startswith('CID: '):
			calldata = line.split('*')
			phonenr = calldata[8]
			print ('You are called by ' + '%s' % str(phonenr))
			notification = Notify()
			notification.showNotification(('%s ' % str(phonenr)) + "calls you...",5000)
		else:
			print line

class NcidClientFactory(ClientFactory):
	protocol = NcidClient

	def clientConnectionFailed(self, connector, reason):
		print ('connection failed: %s' % reason.getErrorMessage())
		notification = Notify()
		notification.showNotification("Connection failed",1000)
		reactor.stop()

	def clientConnectionFailed(self, connector, reason):
		print ('connection lost: %s' % reason.getErrorMessage())
		notification = Notify()
		notification.showNotification("Connection lost",1000)
		reactor.stop()
		
		
		
class MyDaemon(daemon):
#   Overrides run function in daemon
    def run(self):
        print '[+] Initializing...'
#        notification = Notify()
#        notification.showNotification("Initializing",500) # Takes too long to close...
        factory = NcidClientFactory()
        reactor.connectTCP(SERVER_IP, SERVER_PORT, factory)
        print '[+] Started!'
#       notification.showNotification("Started",500) Takes too long to close...
        reactor.run()   
        print '[+] Stopped!'
#       notification.showNotification("Stopped",500) Same here :D

	
if __name__ == '__main__':

    daemon = MyDaemon('/tmp/CallAlert.pid')
    if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        if os.path.isfile('/tmp/CallAlert.pid'):
                            os.remove('/tmp/CallAlert.pid')
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
    else:
                print "Usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)

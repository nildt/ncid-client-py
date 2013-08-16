#!/usr/bin/python -u
# -*- coding: utf-8 -*-
#At the moment only testing...#
'''simple tcp client'''
import pynotify
import time
# apt-get install python-configobj
from configobj import ConfigObj

# apt-get install python-twisted
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from datetime import datetime

CONFIG = ConfigObj('./ncid-client.cfg')
SERVER_IP = CONFIG.get('server_ip', '192.168.2.1')
SERVER_PORT = int(CONFIG.get('server_port', 3333))

class NcidClient(LineReceiver):
	def lineReceived(self, line):
		if line.startswith('CIDLOG:'):
			data = line.split('*')
			date, time, phonenr = data[2], data[4], data[8]
			tstamp_log = datetime.strptime('%s %s' % (date, time), '%d%m%Y %H%M').strftime('%Y-%m-%d %H:%M')
			print ('%s: %s' % (str(tstamp_log), phonenr))
		else:
			print line

class NcidClientFactory(ClientFactory):
	protocol = NcidClient

	def clientConnectionFailed(self, connector, reason):
		print ('connection failed: %s' % reason.getErrorMessage())
		reactor.stop()

	def clientConnectionFailed(self, connector, reason):
		print ('connection lost: %s' % reason.getErrorMessage())
		reactor.stop()
		
class Notify(object):
	def showNotification(self,notification):
		pynotify.init("CallAlertWindow2")
		msg = pynotify.Notification(notification, "Alert", "notification-message-im")
		msg.set_timeout(10000)
		msg.show()

def main():
	print 'initializing...'
	
	pynotify.init("CallAlertWindow")
	msg = pynotify.Notification("Call", "Alert", "notification-message-im")
	msg.set_timeout(10000)
	msg.show()
	time.sleep(1)
	msg.update("Incoming Call", "Es ruft --- an.", "notification-audio-volume-high")
	msg.show()
	
	test = Notify()
	test.showNotification("Test")
	
	factory = NcidClientFactory()
	reactor.connectTCP(SERVER_IP, SERVER_PORT, factory)
	print 'started!'
	reactor.run()
	print 'stopped!'
	
if __name__ == '__main__':
	main()

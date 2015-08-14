# -*- coding: utf-8 -*-

import socket
import sys
import time
import fnmatch
import json
import threading
 

class TCPClient(threading.Thread):
	def __init__(self, parent=None):
		threading.Thread.__init__(self, parent)
		self.recvqueue = []
		self.handlers = []
		self.clientid = 0
		self.isconnected = False
		self.srv = ('192.168.1.89', 9999)
		self.loadconfig()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


	def registersignal(self, handler):
		self.handlers.append(handler)


	def emitsignal(self, signal):
		for hd in self.handlers:
			hd(signal)



	def loadconfig(self):
		readed = json.load(open('config', 'r'))

		self.clientid = readed["clientid"]
		print "client id: %d" % self.clientid

		self.srv = (readed["srvip"],readed["srvport"])
		print "srv: %s" % str(self.srv)



	def run(self):
		while True:
			try:
				if self.isconnected:
					received = self.sock.recv(1024)
					if len(received) > 0:
						self.processdata(received)
			except socket.error as err:
				print("Error on recv: " + str(err))
			finally:
				time.sleep(0.1)
				self.reconnect()



	def reconnect(self):
		if not self.isconnected:
			self.sock.close()
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connectsrv()


		
	def processdata(self, data):
		msgs = [onemsg for onemsg in data.split('@') if len(onemsg) > 0]
		for singlemsg in msgs:
			self.recvqueue.append(singlemsg)
			self.emitsignal("recv()")



	def onconn(self, res):
		print "onconn "+str(res)
		self.isconnected = res
		if res:
			self.start()
			self.senddata("hello server")
		else:
			self.reconnect()



	def onsend(self, res):
		print "onsend "+str(res)
		if not res:
			self.isconnected = False



	def senddata(self, data):
		try:
		    self.sock.send(data)
		    self.onsend(True)
		except socket.error as err:
			self.onsend(False)
			print("Error on send: " + str(err))
			self.sock.close()
		#finally:
			#print("close socket")




	def connectsrv(self):
		try:
			self.sock.connect(self.srv)
			self.onconn(True)
			self.emitsignal("conn(True)")
		except socket.error as err:
			self.onconn(False)
			self.emitsignal("conn(False)")
			print("Error on connect: " + str(err))
			self.sock.close()
		#finally:
			#print("close socket")




class TheApp():
	def __init__(self):
		self.client = TCPClient()
		self.client.registersignal(self.signalhandler)
		self.client.connectsrv()

	def signalhandler(self, signal):
		print "rcv signal: %s" % signal
		if signal == "recv()":
			self.onrecv()
		elif signal == "conn(True)":
			self.onconn(True)
		elif signal == "conn(False)":
			self.onconn(False)
		

	def onconn(self, bresult):
		print "onconn"
		

	def onrecv(self):
		data = self.client.recvqueue[0]
		protoc = [submsg for submsg in data.split("##") if len(submsg) > 0]
		if len(protoc) != 3:
			print "parse data error: %s" % data
		else:
			if int(protoc[0]) == 0 or int(protoc[0]) == self.client.clientid:
				print "data for me:%s" % str(protoc)
				if int(protoc[1]) == 1:
					self.changebg(protoc[2])
				elif int(protoc[1]) == 2:
					self.playaudio(protoc[2])
				elif int(protoc[1]) == 3:
					self.showch(protoc[2])
		self.client.recvqueue.remove(data)

	def zouni(self):
		while True:
			time.sleep(1)



if __name__ == "__main__":

	app = TheApp()
	app.zouni()
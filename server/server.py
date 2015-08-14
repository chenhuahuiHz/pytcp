# -*- coding: utf-8 -*-

import socket
import select
import pickle
import copy
import datetime
import time
from threading import Timer

#charcs = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#index = 0


class CServer:
	def __init__(self, port):
		self.port = port
		self.initServer()
		self.timer = None
		print 'Server started on port %s' % port

	def timerjob(self):
		# do timer job

		self.timer = Timer(1, self.timerjob)
		self.timer.start()

	def initServer(self):
		self.descriptors = []
		# self.srvsock.close()

		self.srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.srvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.srvsock.bind((socket.gethostbyname(socket.gethostname()), self.port))
		self.srvsock.listen(15)
		self.descriptors = [self.srvsock]


	def run(self):
		self.timerjob()
		while 1:
			try:
				(sread, swrite, sexc) = select.select( self.descriptors, [], [] )
				for sock in sread:
					try:
						if sock == self.srvsock:
							self.acceptconnection()
						else:
							data = sock.recv(1024)
							if data == '':
								sock.close()
								self.descriptors.remove(sock)
							else:
								host,port = sock.getpeername()
								self.processrecv(sock, host, port, data)

					except socket.error as err:
						print("Error on run: " + str(err))
						sock.close
						self.descriptors.remove(sock)
			except select.error as err:
				print("Error on select: " + str(err))
				self.initServer()


	def processrecv(self, sock, host, port, data):
		print("recv: "+data)
		sock.send(data+" ack")
		datas = [onedata for onedata in data.split("##") if len(onedata) > 0]


	def acceptconnection(self):
		newsock, (remhost, remport) = self.srvsock.accept()
		print("new connection from "+remhost)
		self.descriptors.append(newsock)

	def broadcast(self, data, omit_sock, toself):
		# time.sleep(0.1)
		#print "broadcast:%s" % data
		for sock in self.descriptors:
			if sock != self.srvsock:
				if not toself and sock == omit_sock:
					continue
				sock.send(data)




if __name__ == "__main__":
    PORT = 9999
    server = CServer(PORT)
    server.run()

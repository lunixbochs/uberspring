import socket, time

class UDPClient:
	def __init__(self):
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
	def send(self, packet):
		self.conn.sendto(packet, ('192.168.1.6', 8452))
	
	def recv(self):
		return self.conn.recvfrom(1024)
		
s = UDPClient()
s.send('\x00\x00\x00\x00\xff\xff\xff\xff\x00\x19:\x00Cranbury\x00\x000.80+.0.0 (0.80.0-42-gecd82e0-cmake-mingw32)\x00')
while True:
	print s.recv()
	time.sleep(1)
time.sleep(9001)
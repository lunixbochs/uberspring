import socket, traceback, binascii, time, struct, zlib, select
# possibly implement ALL PACKET PARSING AND CONSTRUCTION in a single separate module...

from netprotocol import NetProtocol as Protocol

host = '127.0.0.1'
port = 8452

#const unsigned UDPConnection::hsize = 9;
#const unsigned UDPMaxPacketSize = 4096;
#const int MaxChunkSize = 254;
#const int ChunksPerSec = 30;

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))

class UDPConnection:
	# headerSize = 9 # just hardcoded
	maxPacketSize = 4096
	
	def __init__(self, sock, address):
		self.socket = sock
		self.address = address
		
		self.lastNakTime = -1
		self.lastSendTime = -1
		self.lastReceiveTime = time.time()
		self.lastInOrder = -1
		self.waitingPackets = {}
		self.messageQueue = []
		self.unackedPackets = []
		self.outgoingData = []
		
		self.firstUnacked = 0
		self.currentNum = 0
		self.lastNak = -1
		
		self.fragmentBuffer = ''
		
		self.mtu = 500
		
		self.proto = Protocol()
	
	def sendData(self, data):
		if data: self.outgoingData.append(data)
	
	def peek(self, ahead):
		if ahead < len(self.messageQueue):
			return self.messageQueue[ahead]
		else:
			return False
	
	def getData(self):
		if self.messageQueue:
			return self.messageQueue.pop(0)
		else:
			return False
	
	def update(self):
		#print 'update()'
		curTime = time.time()
		force = False
		
		if self.lastInOrder < 0 and self.lastSendTime < curTime-1 and self.unackedPackets:
			self.sendRawPacket(self.unackedPackets[0], 0)
			self.lastSendTime = curTime
			force = True
		
		if self.lastSendTime < curTime-5 and self.lastInOrder >= 0:
			force = True
		elif self.lastSendTime < curTime - float(200)/1000 and self.waitingPackets:
			force = True
		
		self.flush(force)
			
	
	def processRawPacket(self, packet):
		if len(packet) < 9: return
		
		print '<- %s' % packet
		self.lastReceiveTime = time.time()
		
		# int packetNum = *(int*)packet->data; # maybe write a python function to do it like this...
		# unpack.int(data[4:]) will take return an int from the beginning... 
		# unpack.short(data) same thing... possibly make an unpack or packet class...
		# make it continue where it left off :)
		packetNum = struct.unpack('<i', packet[:4])[0]
		ack = struct.unpack('<i', packet[4:8])[0]
		nak = struct.unpack('<B', packet[8])[0]
		
		self.ackPackets(ack)
		
		if nak > 0: # we have lost $nak packets
			nak_abs = nak + self.firstUnacked - 1
			if nak_abs > self.currentNum: # we got a nak for packets we never sent, give an error message
				pass
			elif nak_abs != self.lastNak or self.lastNakTime < self.lastReceiveTime - float(100)/1000:
				self.lastNak = nak_abs
				self.lastNakTime = self.lastReceiveTime
				for i in xrange(self.firstUnacked, nak_abs+1):
					self.sendRawPacket(self.unackedPackets[i-firstUnacked], i)
		
		# need to figure out what next parts actually do and implement them
		# up till waitingPackets.insert()
		if packetNum in self.waitingPackets or packetNum < self.lastInOrder:
			print packetNum, self.lastInOrder
			print 'duplicate packet'
			return # duplicate packet
		self.waitingPackets[packetNum] = packet[9:]
		# print binascii.hexlify(packet[9:])
		
		# process half-baked packets, possibly should be its own function.. though I suppose it'll be one of the top levels of processing
		while (self.lastInOrder+1 in self.waitingPackets):
			if self.fragmentBuffer:
				packet = self.fragmentBuffer + self.waitingPackets[self.lastInOrder+1]
			else:
				packet = self.waitingPackets[self.lastInOrder+1]
			
			self.lastInOrder += 1
			del self.waitingPackets[self.lastInOrder]
			
			while packet:
				msg_id = ord(packet[0])
				print 'Message ID: %s' % msg_id
				length = self.proto.getLength(msg_id)
				if length != 0:
					if length < 0:
						if len(packet) >= -length: # do we have enough data in the buffer to read the length of the message?
							if length == -1: # length is a uchar
								struct.unpack('<B', packet[1])
							elif length == -2: # length is short
								struct.unpack('<H', packet[1:3])
						else:
							self.fragmentBuffer = packet
							break
					
					# is the complete message in the buffer?
					if len(packet) >= length:
						# yes -> add to message queue and keep going
						self.messageQueue.append(packet[:length])
						packet = packet[length:]
					else:
						# no -> store fragment and break
						self.fragmentBuffer = packet
						break
				else:
					print 'Invalid message ID: %i' % msg_id
					packet = packet[1:] # bad message id - this could cause serious problems... possibly need to drop this packet completely...
	
	def flush(self, forced):
		curTime = time.time()
		
		outgoingLength = 0
		for item in self.outgoingData:
			outgoingLength += len(item)
		if forced or (self.outgoingData and (self.lastSendTime < (curTime - .200 + float(outgoingLength) / 10))):
			self.lastSendTime = time.time()
			
			# manually fragment packets to respect mtu, to fix a bug where players drop out of the game when someone gives a large order
			
			buffer = ''
			
			while self.outgoingData:
				packet = self.outgoingData[0]
				length = min(self.mtu, len(packet))
				buffer = packet[:length]
				if length == len(packet):
					self.outgoingData.pop(0)
				else:
					self.outgoingData[0] = packet[:length]
				self.sendRawPacket(buffer, self.currentNum)
				self.unackedPackets.append(buffer)
				self.currentNum += 1
			else:
				if forced:
					buffer = ''
					self.sendRawPacket(buffer, self.currentNum)
					self.unackedPackets.append(buffer)
					self.currentNum += 1

	def checkTimeout(self):
		timeout = 45 if (self.lastInOrder < 0) else 30
		return True if (self.lastReceiveTime+timeout) < time.time() else False
	
	def setMTU(self, mtu):
		if (mtu > 300) and (mtu < self.maxPacketSize):
			self.mtu = mtu
	
	def ackPackets(self, nextAck):
		while (nextAck >= self.firstUnacked) and (self.unackedPackets):
			self.unackedPackets.pop(0)
			self.firstUnacked += 1
	
	def sendRawPacket(self, data, packetNum):
		print '-> %s' % data
		#packetNum = self.currentNum
		#self.currentNum += 1
		packet = struct.pack('<ii', packetNum, self.lastInOrder)
		if self.waitingPackets and sorted(self.waitingPackets.keys())[-1] == self.lastInOrder+1:
			nak = (sorted(self.waitingPackets.keys())[0] - 1) - self.lastInOrder
			assert nak >= 0
			packet += struct.pack('<B', nak)
		else:
			packet += struct.pack('<B', 0)
		
		packet += data
		print str(packet)
		self.socket.sendto(packet, self.address)
		#f = open('packets.txt', 'a')
		#f.write(packet+'\n\nseparator\n\n')
		#f.close()

class GameData:
	def __init__(self, setupText, mapChecksum, modChecksum, randomSeed):
		self.setupText = setupText
		self.mapChecksum = mapChecksum
		self.modChecksum = modChecksum
		self.randomSeed = randomSeed
	
	def pack(self):
		compressedText = zlib.compress(self.setupText)
		compressedSize = len(compressedText)
		size = 5 + compressedSize + 12
		packet = struct.pack('<BHH', 52, size, compressedSize)
		packet += compressedText
		packet += struct.pack('<3i', self.mapChecksum, self.modChecksum, self.randomSeed)
		f = open('gamedata.dat', 'rb')
		packet = f.read()
		f.close()
		return packet

f = open('setupText.txt', 'r')
setupText = f.read()
f.close()
gamedata = GameData(setupText, 1150274397, 1456644190, 20262)

connections = []
s.setblocking(0)
outputready = False

'''
a = UDPConnection(1, 1)
packet = struct.pack('<iiB', 0, 0, 0) + gamedata.pack()
a.processRawPacket(packet)
data = a.getData()

cmd = data[0]
cmd = 'gamedata'
data = data[1:]
size, compressedSize = struct.unpack('<HH', data[:4])
setupText = zlib.decompress(data[4:compressedSize+4])
data = data[compressedSize+4:]
#print data
#print __import__('binascii').hexlify(data)
#return
#mapName, modName, data = data.split('\0', 2)
#print mapName, modName
if len(data) == 12: # 0.80 or later
	mapChecksum, modChecksum, randomSeed = struct.unpack('<3i', data)

f = open('gamedata.txt', 'wb')
f.write(setupText)
'''

while 1:
	try:
		for conn in connections:
			if conn.outgoingData:
				outputready = True
				break
		else:
			outputready = False
				
		incoming, outgoing, erroring = select.select([s], [], [], (0 if outputready else 1))
		for s in incoming:
			message, address = s.recvfrom(4096) # mtu should keep it on 
			for conn in connections:
				if conn.address == address:
					conn.processRawPacket(message)
					data = conn.getData()
					if data:
						print data
					break
			else: # only accept new connections if we are accepting new connections ;) # gotta add a var when I transition to udplistener or whatever I'm going to call it.
				conn = UDPConnection(s, address)
				connections.append(conn)
				f = open('packet.txt', 'w')
				f.write(message)
				f.close()
				conn.processRawPacket(message)
				packet = conn.getData()
				print 'parsing', packet
				if packet and len(packet) >= 3 and ord(packet[0]) == 25:
					name, passwd, version = packet[3:].split('\0',2)
					print 'Connection attempt from %s' % name
					print ' -> Address: %s' % address[0]
					# <todo> start using player list
					if False: # <todo> check playernum over size of players
						if False: # <todo> if demoreader or allowAdditionalPlayers:
							isFromDemo = False
							name = name
							spectator = True
							team = 0
							# <todo> add to players list
						else:
							print ' -> %s not found in script, rejecting connection attempt' % name
							break
					
					# <todo> a password check here
					conn.sendData(gamedata.pack())
					#conn.sendData(chr(0))
				else:
					print 'Connection rejected - packet too short %s' % str(address)
				
		for conn in connections:
			# gotta know if the player is no longer connected
				# continue
			if conn.checkTimeout():
				# send a timeout message
				# send other stuffs
				continue
			conn.update()
			
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		traceback.print_exc()
		time.sleep(1)
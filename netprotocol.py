from constants import *

import struct

# PackPacket in rts/system/net/PackPacket.cpp
# RawPacket in rts/system/net/RawPacket.cpp
class Packet:
	def __init__(self, length, msgID=None, msgType=None):
		self.data = ''
		self.pos = 0
		self.type = msgType
		
		if msgID:
			self.pack_uchar(msgID)
	
	def pack_raw(self, data):
		if len(self.data) + len(data) > self.length:
			print 'netcode error: too much data in packet of type %s' % (self.type)
		else:
			self.data += data
	
	def pack_string(self, string):
		if '\0' in string:
			print 'netcode warning: text must not contain "\\0" inside, truncating'
			string = string.split('\0', 1)[0]
		
		remaining = self.length - len(self.data)
		if len(string) + 1 > remaining:
			print 'netcode warning: string data truncated in packet'
			string = string[:remaining]
		
		string += '\0'
		self.pack_raw(string)
	
	def struct_pack(self, fmt, var):
		self.pack_raw(struct.pack(fmt, var))
	
	def pack_uchar(self, uchar):
		self.struct_pack('B', uchar)
	
	def pack_uint16(self, uint):
		self.struct_pack('H', uint)
	
	def pack_uint32(self, uint):
		self.struct_pack('I', uint)

	def pack_int(self, var):
		self.struct_pack('i', var)

	def pack_float(self, var):
		self.struct_pack('f', var)

# CBaseNetProtocol in rts/system/BaseNetProtocol.cpp
class NetProtocol:
	def SendKeyFrame(self, frameNum):
		packet = Packet(5, NETMSG_KEYFRAME, msgType='NETMSG_KEYFRAME')
		packet.pack_uchar(frameNum)
		return packet
	
	def SendNewFrame(self):
		return Packet(1, NETMSG_NEWFRAME, msgType='NETMSG_NEWFRAME')
	
	def SendQuit(self, reason):
		size = 3 + len(reason) + 1
		packet = Packet(size, NETMSG_QUIT, msgType='NETMSG_QUIT')
		packet.pack_uint16(size)
		packet.pack_string(reason)
		return packet
	
	def SendStartPlaying(self, countdown):
		packet = Packet(5, NETMSG_STARTPLAYING, msgType='NETMSG_STARTPLAYING')
		packet.pack_uint32(countdown)
		return packet
	
	def SendSetPlayerNum(self, myPlayerNum):
		packet = Packet(2, NETMSG_SETPLAYERNUM, msgType='NETMSG_SETPLAYERNUM')
		packet.pack_uchar(myPlayerNum)
		return packet
	
	def SendPlayerName(self, playerNum, playerName):
		size = 3 + len(playerName) + 1
		packet = Packet(size, NETMSG_PLAYERNAME, msgType='NETMSG_PLAYERNAME')
		packet.pack_uchar(playerNum)
		packet.pack_string(playerName)
		return packet
	
	def SendRandSeed(self, randSeed):
		packet = Packet(5, NETMSG_RANDSEED, msgType='NETMSG_RANDSEED')
		packet.pack_uint32(randSeed)
		return packet
	
	def SendGameID(self, gameID):
		packet = Packet(17, NETMSG_GAMEID, msgType='NETMSG_GAMEID')
		gameID = gameID[:16].ljust(17, '\0')
		packet.pack_raw(gameID)
		return packet
	
	def SendPathCheckSum(self, playerNum, checksum):
		packet = Packet(6, NETMSG_PATH_CHECKSUM, msgType='NETMSG_PATH_CHECKSUM')
		packet.pack_uchar(playerNum)
		packet.pack_uint32(checksum)
		return packet
	
	def SendCommand(self, playerNum, id, options, params):
		size = 9 + len(params) * 4
		packet = Packet(size, NETMSG_COMMAND, msgType='NETMSG_COMMAND')
		packet.pack_uint16(size)
		packet.pack_uchar(playerNum)
		packet.pack_int32(id)
		packet.pack_uchar(options)
		for item in params:
			packet.pack_float(item)
		
		return packet
	
	def SendSelect(self, playerNum, selectedUnitIDs):
		size = 4 + len(selectedUnitIDs) * 2
		packet = Packet(size, NETMSG_SELECT, msgType='NETMSG_SELECT')
		packet.pack_uint16(size)
		packet.pack_uchar(playerNum)
		
		for item in selectedUnitIDs:
			packet.pack_uint16(size)
		
		return packet
	
	def SendPause(self, playerNum, bPaused):
		packet = Packet(3, NETMSG_PAUSE, msgType='NETMSG_PAUSE')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(bPaused)
		return packet
	
	def SendAICommand(self, playerNum, unitID, id, options, params):
		size = 11 + len(params) * 4
		packet = Packet(size, NETMSG_AICOMMAND, msgType='NETMSG_AICOMMAND')
		packet.pack_uint16(size)
		packet.pack_uchar(playerNum)
		packet.pack_uint16(unitID)
		packet.pack_int32(id)
		packet.pack_uchar(options)
		for item in params:
			packet.pack_float(item)
		
		return packet
	
	def SendAIShare(self, playerNum, sourceTeam, destTeam, metal, energy, unitIDs):
		size = 14 + len(unitIDs) * 2
		
		packet = Packet(size, NETMSG_AISHARE, msgType='NETMSG_AISHARE')
		packet.pack_uint16(size)
		packet.pack_uchar(playerNum)
		packet.pack_uchar(sourceTeam)
		packet.pack_uchar(destTeam)
		packet.pack_float(metal)
		packet.pack_float(energy)
		for unit in unitIDs:
			packet.pack_uint16(unit)
		
		return packet
	
	def SendUserSpeed(self, playerNum, userSpeed):
		packet = Packet(6, NETMSG_USER_SPEED, msgType='NETMSG_USER_SPEED')
		packet.pack_uchar(playerNum)
		packet.pack_float(userSpeed)
		return packet
	
	def SendInternalSpeed(self, internalSpeed):
		packet = Packet(5, NETMSG_INTERNAL_SPEED, msgType='NETMSG_INTERNAL_SPEED')
		packet.pack_float(internalSpeed)
		return packet
	
	def SendCPUUsage(self, cpuUsage):
		packet = Packet(5, NETMSG_CPU_USAGE, msgType='NETMSG_CPU_USAGE')
		packet.pack_float(internalSpeed)
		return packet
	
	def SendCustomData(self, playerNum, dataType, dataValue):
		packet = Packet(7, NETMSG_CUSTOM_DATA, msgType='NETMSG_CUSTOM_DATA')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(dataType)
		packet.pack_int(dataValue)
		return packet
	
	def SendSpeedControl(self, playerNum, speedCtrl):
		return self.SendCustomData(playerNum, CUSTOM_DATA_SPEEDCONTROL, speedCtrl)
	
	def SendLuaDrawTime(self, playerNum, mSec):
		return self.SendCustomData(playerNum, CUSTOM_DATA_LUADRAWTIME, mSec)
	
	def SendDirectControl(self, playerNum):
		packet = Packet(2, NETMSG_DIRECT_CONTROL, msgType='NETMSG_DIRECT_CONTROL')
		packet.pack_uchar(playerNum)
		return packet
	
	def SendDirectControlUpdate(self, playerNum, status, heading, pitch):
		packet = Packet(7, NETMSG_DC_UPDATE, msgType='NETMSG_DC_UPDATE')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(status)
		packet.pack_uint16(heading)
		packet.pack_uint16(pitch)
		return packet
	
	def SendAttemptConnect(self, name, passwd, version, reconnect):
		size = 7 + len(name) + len(passwd) + len(version)
		packet = Packet(size, NETMSG_ATTEMPTCONNECT, msgType='NETMSG_ATTEMPTCONNECT')
		packet.pack_uint16(size)
		packet.pack_string(name)
		packet.pack_string(passwd)
		packet.pack_string(version)
		packet.pack_uchar(reconnect)
		return packet
	
	def SendShare(self, playerNum, shareTeam, bShareUnits, shareMetal, shareEnergy):
		packet = Packet(12, NETMSG_SHARE, msgType='NETMSG_SHARE')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(shareTeam)
		packet.pack_uchar(bShareUnits)
		packet.pack_float(shareMetal)
		packet.pack_float(shareEnergy)
		return packet
	
	def SendSetShare(self, playerNum, team, metalShareFraction, energyShareFraction):
		packet = Packet(11, NETMSG_SETSHARE, msgType='NETMSG_SETSHARE')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(team)
		packet.pack_float(metalShareFraction)
		packet.pack_float(energyShareFraction)
		return packet
	
	def SendSendPlayerStat(self):
		return Packet(1, NETMSG_SENDPLAYERSTAT, msgType='NETMSG_SENDPLAYERSTAT')
	
	def SendPlayerStat(self, playerNum, currentStats):
		packet = Packet(2 + 0, NETMSG_PLAYERSTAT, msgType='NETMSG_PLAYERSTAT')
		packet.pack_uchar(playerNum)
		return packet
	
	def SendGameOver(self):
		return Packet(1, NETMSG_GAMEOVER, msgType='NETMSG_GAMEOVER')
	
	def SendMapErase(self, playerNum, x, z):
		packet = Packet(8, NETMSG_MAPDRAW, msgType='NETMSG_MAPDRAW')
		packet.pack_uchar(8) # size
		packet.pack_uchar(playerNum)
		packet.pack_uint16(x)
		packet.pack_uint16(z)
		return packet
	
	def SendMapDrawPoint(self, playerNum, x, z, label, fromLua):
		size = 9 + len(label) + 1
		packet = Packet(size, NETMSG_MAPDRAW, msgType='NETMSG_MAPDRAW')
		packet.pack_uchar(size)
		packet.pack_uchar(playerNum)
		packet.pack_uchar(MAPDRAW_POINT)
		packet.pack_uint16(x)
		packet.pack_uint16(z)
		packet.pack_uchar(fromLua)
		packet.pack_string(label)
		return packet
	
	def SendMapDrawLine(self, playerNum, x1, z1, x2, z2, fromLua):
		packet = Packet(13, NETMSG_MAPDRAW, msgType='NETMSG_MAPDRAW')
		packet.pack_uchar(13) # size
		packet.pack_uchar(playerNum)
		packet.pack_uchar(MAPDRAW_LINE)
		packet.pack_uint16(x1)
		packet.pack_uint16(z1)
		packet.pack_uint16(x2)
		packet.pack_uint16(z2)
		packet.pack_uchar(fromLua)
		return packet
	
	def SendSyncResponse(self, frameNum, checksum):
		packet = Packet(9, NETMSG_SYNCRESPONSE, msgType='NETMSG_SYNCRESPONSE')
		packet.pack_int(frameNum)
		packet.pack_uint32(checksum)
		return packet
	
	def SendSystemMessage(self, playerNum, message):
		if len(message) > 65000:
			message = message[:64997] + '...'
		
		size = 4 + len(message) + 1
		packet = Packet(size, NETMSG_SYSTEMMSG, msgType='NETMSG_SYSTEMMSG')
		packet.pack_uint16(size)
		packet.pack_uchar(playerNum)
		packet.pack_string(message)
		return packet
	
	# @signature(uchar, uchar, uchar, float, float, float)
	def SendStartPos(self, playerNum, teamNum, ready, x, y, z):
		packet = Packet(16, NETMSG_STARTPOS, msgType='NETMSG_STARTPOS')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(teamNum)
		packet.pack_uchar(ready)
		packet.pack_float(x)
		packet.pack_float(y)
		packet.pack_float(z)
		return packet
	
	# @signature(uchar, float, int)
	def SendPlayerInfo(self, playerNum, cpuUsage, ping):
		packet = Packet(10, NETMSG_PLAYERINFO, msgType='NETMSG_PLAYERINFO')
		packet.pack_uchar(playerNum)
		packet.pack_float(cpuUsage)
		packet.pack_int(ping)
		return packet
	
	# @signature(uchar, uchar)
	def SendPlayerLeft(self, playerNum, bIntended):
		packet = Packet(3, NETMSG_PLAYERLEFT, msgType='NETMSG_PLAYERLEFT')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(bIntended)
		return packet
	
	# @signature(uchar, uchar, uint16, uchar, uchar_vector)
	def SendLuaMsg(self, playerNum, script, mode, msg):
		size = 7 + len(msg)
		packet = Packet(size, NETMSG_LUAMSG, msgType='NETMSG_LUAMSG')
		packet.pack_uchar(size)
		packet.pack_uchar(playerNum)
		packet.pack_uint16(script)
		packet.pack_uchar(mode)
		
		packet.pack_raw(msg)
		
		# packet.signature(uchar, uchar, uint16, uchar, uchar_vector)
		# packet.pack(size, playerNum, script, mode, msg)
		return packet
	
	def SendGiveAwayEverything(self, playerNum, giveToTeam, takeFromTeam):
		packet = Packet(5, NETMSG_TEAM, msgType='NETMSG_TEAM')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(TEAMMSG_GIVEAWAY)
		packet.pack_uchar(giveToTeam)
		packet.pack_uchar(takeFromTeam)
		
		# packet.signature(uchar, uchar, uchar, uchar)
		# packet.pack(playerNum, TEAMMSG_GIVEAWAY, giveToTeam, takeFromTeam)
		return packet
	
	def SendResign(self, playerNum):
		packet = Packet(5, NETMSG_TEAM, msgType='NETMSG_TEAM')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(TEAMMSG_RESIGN)
		packet.pack_uchar(0)
		packet.pack_uchar(0)
		
		# packet.signature(uchar, uchar, uchar, uchar)
		# packet.pack(playerNum, TEAMMSG_RESIGN, 0, 0)
		return packet
		
	def SendJoinTeam(self, playerNum, wantedTeamNum):
		packet = Packet(5, NETMSG_TEAM, msgType='NETMSG_TEAM')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(TEAMMSG_JOIN_TEAM)
		packet.pack_uchar(wantedTeamNum)
		packet.pack_uchar(0)
		
		# packet.signature(uchar, uchar, uchar, uchar)
		# packet.pack(playerNum, TEAMMSG_JOIN_TEAM, wantedTeamNum, 0)
		return packet
	
	def SendTeamDied(self, playerNum, whichTeam):
		packet = Packet(5, NETMSG_TEAM, msgType='NETMSG_TEAM')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(TEAMMSG_TEAM_DIED)
		packet.pack_uchar(whichTeam)
		packet.pack_uchar(0)
		
		# packet.signature(uchar, uchar, uchar)
		# packet.pack(playerNum, TEAMMSG_JOIN_TEAM, wantedTeamNum, 0)
		return packet
	
	def SendAICreated(self, playerNum, whichSkirmishAI, team, name):
		size = 8 + len(name) + 1
		packet = Packet(size, NETMSG_AI_CREATED, msgType='NETMSG_AI_CREATED')
		packet.pack_uchar(size)
		packet.pack_uchar(playerNum)
		packet.pack_uint32(whichSkirmishAI)
		packet.pack_uchar(team)
		packet.pack_string(name)
		
		# packet.signature(uchar, uchar, uint32, uchar, string)
		# packet.pack(size, playerNum, whichSkirmishAI, team, name)
		return packet
	
	def SendAIStateChanged(self, playerNum, whichSkirmishAI, newState):
		packet = Packet(7, NETMSG_AI_STATE_CHANGED, msgType='NETMSG_AI_STATE_CHANGED')
		packet.pack_uchar(playerNum)
		packet.pack_uint32(whichSkirmishAI)
		packet.pack_uchar(newState)
		
		# packet.signature(uchar, uint32, uchar)
		# packet.pack(playerNum, whichSkirmishAI, newState)
		return packet
	
	def SendSetAllied(self, playerNum, whichAllyTeam, state):
		packet = Packet(4, NETMSG_ALLIANCE, msgType='NETMSG_ALLIANCE')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(whichAllyTeam)
		packet.pack_uchar(state)
		
		# packet.signature(uchar, uchar, uchar)
		# packet.pack(playerNum, whichAllyTeam, state)
		return packet
	
	def SendRegisterNetMsg(self, playerNum, msgID):
		packet = Packet(3, NETMSG_REGISTER_NETMSG, msgType='NETMSG_REGISTER_NETMSG')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(msgID)
		
		# packet.signature(uchar, uchar)
		# packet.pack(playerNum, msgID)
		return packet
	
	def SendUnRegisterNetMsg(self, playerName, msgID):
		packet = Packet(3, NETMSG_UNREGISTER_NETMSG, msgType='NETMSG_UNREGISTER_NETMSG')
		packet.pack_uchar(playerNum)
		packet.pack_uchar(msgID)
		
		# packet.signature(uchar, uchar)
		# packet.pack(playerNum, msgID)
		return packet
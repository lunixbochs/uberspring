import sys, os, random

class PyClientSetup:
	'''basic client setup'''
	defaultHostPort = 8452

	def __init__(self, gameSetup):
		self.myPlayerName = ''
		self.myPasswd = ''

		self.hostip = ''
		self.hostport = 0
		self.sourceport = 0
		self.autohostport = 0

		self.isHost = True

class PyGameSetup:
	'''stores the game script'''
	

class PyGameData:
	'''stores the game data'''
	def __init__(self):
		this.modHash = ''
		this.mapHash = ''
		this.randSeed = ''

class PyGameServer:
	'''the actual server instance'''
	serverPlayer = 255; # When the Server generates a message, this value is used as the sending player-number.
	
	def __init__(self, settings, onlyLocal, newGameData, setup):
		self.serverStartTime = 0 # spring_gettime() << figure out what this does exactly
		self.lastUpdate = serverStartTime
		self.lastPlayerInfo = serverStartTime
		self.delayedSyncResponseFrame = 0
		self.syncErrorFrame = 0
		self.syncWarningFrame = 0
		self.serverFrameNum = 0
		self.timeLeft = 0
		self.modGameTime = 0.0
		self.quitServer = False
		self.hasLocalClient = False
		self.localClientNumber = 0
		self.isPaused = False
		self.userSpeedFactor = 1.0
		self.internalSpeed = 1.0
		self.gamePausable = True
		self.noHelperAIs = False
		self.allowSpecDraw = True
		self.cheating = False
		self.sentGameOverMsg = False
		
		# figure out what spring_notime does
		'''
		spring_notime(gameStartTime);
		spring_notime(gameEndTime);
		spring_notime(readyTime);
		'''
		
		self.medianCpu = 0.0
		self.medianPing = 0
		self.enforceSpeed = (!setup.hostDemo and configHandler.EnforceGameSpeed) # figure out what confighandler.Get() does
		
		self.allowAdditionalPlayers = configHandler.AllowAdditionalPlayers
		
		'''
		if (!onlyLocal)
			UDPNet.reset(new netcode::UDPListener(settings->hostport));

		if (settings->autohostport > 0) {
			AddAutohostInterface(settings->autohostport);
		}
		
		rng.Seed(newGameData->GetSetup().length());
		Message(str( format(ServerStart) %settings->hostport));
		'''
		
		self.lastTick = 0 # spring_gettime();
		
		self.maxUserSpeed = setup.maxSpeed
		self.minUserSpeed = setup.minSpeed
		self.noHelperAIs = setup.noHelperAIs
		
		'''
		gameData.reset(newGameData);
		if (setup->hostDemo)
		{
			Message(str( format(PlayingDemo) %setup->demoName ));
			demoReader.reset(new CDemoReader(setup->demoName, modGameTime+0.1f));
		}
		
		players.resize(setup->playerStartingData.size());
		std::copy(setup->playerStartingData.begin(), setup->playerStartingData.end(), players.begin());

		teams.resize(setup->teamStartingData.size());
		std::copy(setup->teamStartingData.begin(), setup->teamStartingData.end(), teams.begin());
		'''
		
		restrictedActions = ['kick', 'kickbynum', 'setminspeed', 'nopause', 'nohelp', 'cheat', 'godmode', 'globallos', 'nocost', 'forcestart', 'nospectatorchat', 'nospecdraw', 'reloadcob', 'devlua', 'editdefs', 'luagaia', 'singlestep']
		if demoReader: pass # RegisterAction('skip')
		commandBlacklist.append('skip')
		
		'''
		#ifdef DEDICATED
			demoRecorder.reset(new CDemoRecorder());
			demoRecorder->SetName(setup->mapName);
			demoRecorder->WriteSetupText(gameData->GetSetup());
			const netcode::RawPacket* ret = gameData->Pack();
			demoRecorder->SaveToDemo(ret->data, ret->length, modGameTime);
			delete ret;
		#endif
		
		// AIs do not join in here, so just set their teams as active
		for (size_t i = 0; i < setup->teamStartingData.size(); ++i)
		{
			const SkirmishAIData* sad = setup->GetSkirmishAIDataForTeam(i);
			if (sad != NULL)
			{
				teams[i].leader = sad->hostPlayerNum;
				teams[i].active = true;
				teams[i].isAI = true;
			}
		}

		thread = new boost::thread(boost::bind<void, CGameServer, CGameServer*>(&CGameServer::UpdateLoop, this));
		'''
		
		
	def AddLocalClient(self, name, version):
		pass
		'''
		hasLocalClient = true;
		localClientNumber = BindConnection(myName, "", myVersion, true, boost::shared_ptr<netcode::CConnection>(new netcode::CLocalConnection()));
		'''
	
	def AddAutohostInterface(self, remotePort):
		pass
		'''
		if (!hostif)
		{
			hostif.reset(new AutohostInterface(remotePort));
			hostif->SendStart();
			Message(str(format(ConnectAutohost) %remotePort));
		}
		'''
		
	def PostLoad(self, lastTic, serverFrameNum): # set frame after loading - no checks are done, so be careful.
		pass
		self.lastTick = lastTick
		self.serverFrameNum = serverFrameNum
		
	def CreateNewFrame(self, fromServerThread, fixedFrameTime): pass
	def WaitsOnCon(self): pass
	def GameHasStarted(self): pass
	def GameSetPausable(self, pausable): pass
	def HasDemo(self): pass # do we have a demo reader?
	def HasFinished(self): pass # is the server still running?
	
	# private
	
	def GotChatMessage(self, msg): pass
	def KickPlayer(self, playerNum): pass
	def BindConnection(self, name, passwd, version, isLocal, link): pass
	def CheckForGameStart(self, forced=False): pass
	def StartGame(self): pass
	def UpdateLoop(self): pass
	def Update(self): pass
	def ProcessPacket(self, playernum, packet): pass
	def CheckSync(self): pass
	def ServerReadNet(self): pass
	def CheckForGameEnd(self): pass
	
	def GenerateAndSendGameID(self): pass # generate a unique game identifier and send it to all clients
	def GetPlayerNames(self, indicies): pass
	
	def SendDemoData(self, skipping=False): pass # read data from demo and send it to clients
	
	def Broadcast(self, packet): pass
	def SkipTo(self, targetFrame): # if you are watching a demo, this will push out all data until targetFrame to all clients
		pass
		'''if (targetframe > serverframenum && demoReader)
		{
			CommandMessage msg(str( boost::format("skip start %d") %targetframe ), SERVER_PLAYER);
			Broadcast(boost::shared_ptr<const netcode::RawPacket>(msg.Pack()));
			// fast-read and send demo data
			while (serverframenum < targetframe && demoReader)
			{
				modGameTime = demoReader->GetNextReadTime()+0.1f; // skip time
				SendDemoData(true);
				if (serverframenum % 20 == 0 && UDPNet)
					UDPNet->Update(); // send some data (otherwise packets will grow too big)
			}
			CommandMessage msg2("skip end", SERVER_PLAYER);
			Broadcast(boost::shared_ptr<const netcode::RawPacket>(msg2.Pack()));

			if (UDPNet)
				UDPNet->Update();
			lastUpdate = spring_gettime();
			isPaused = true;
		}
		else
		{
			// allready passed
		}
		'''
		
	def Message(self, message, broadcast=True): pass
	
	# game status variables
	quitServer = False
	serverframenum = 0
	serverStartTime = 0
	readyTime = 0
	gameStartTime = 0
	gameEndTime = 0 # tick when game end was detected
	
	sendGameOverMsg = False
	lastTick = 0
	timeLeft = 0.0
	lastPlayerInfo = 0
	lastUpdate = 0
	modGameTime = 0.0
	
	isPaused = False
	userSpeedFactor = 0.0
	internalSpeed = 0.0
	cheating = False
	
	players = []
	teams = []
	
	medianCpu = 0.0
	medianPing = 0
	enforceSpeed = 0
	
	gamePausable = False
	
	setup = {}
	gameData = {}
	
	maxUserSpeed = 0.0
	minUserSpeed = 0.0
	
	noHelperAIs = False
	allowSpecDraw = True
	allowAdditionalPlayers = False
	
	syncErrorFrame = 0
	syncWarningFrame = 0
	delayedSyncResponseFrame = 0
	
	def InternalSpeedChange(self, newSpeed): pass
	def UserSpeedChange(self, newSpeed, player): pass
	
	hasLocalClient = False
	localClientNumber = 0
	
	def RestrictedAction(self, action): pass
	
	commandBlacklist = [] # if the server receives a command, it will be forwarded to clients if not in this list
	
	demoReader = {}
	demoRecorder = {}
	
	syncCheckTimeout = 300 # frames until a sync check will time out and a warning is issued
	syncCheckMsgTimeout = 400 # used to prevent msg spam

	gameStartDelay = 4 # msecs to wait until the game starts after all players are ready
	playerInfoTime = 2 # the time interval in msec for sending player statistics to each client
	serverTimeout = 30 # msecs to wait until the timeout condition (nonactive clients) activates
	serverKeyframeInterval = 16 # every nth frame will be a keyframe (and contain the server's framenumber)
	

class GameTeam:
	'''represents a single team'''
	def __init__(self):
		self.active = False;
		

print 'if you find any errors, report them to aegis.'

# parse config file
print sys.argv

if len(sys.argv) > 1:
	pass
else:
	print 'usage: spring-dedicated <full_path_to_script>'


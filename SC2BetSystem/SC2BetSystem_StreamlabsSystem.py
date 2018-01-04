"""
###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
"""

#---------------------------------------
#	Import Libraries
#---------------------------------------
import sys
import datetime
import json
import os
import time
from collections import defaultdict
from collections import OrderedDict
import threading
import clr
import codecs

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "SCII - Betting System"
Website = "https://www.brains-world.eu"
Description = "Automatic Betting System for StarCraft II"
Creator = "Brain & Burny"
Version = "1.2.0"

#---------------------------------------
#	Set Variables
#---------------------------------------
debuggingMode = True
gameUrl = "http://localhost:6119/game"
uiUrl = "http://localhost:6119/ui"
timeSinceLastUpdate = time.time()
configFile = "SC2BetSystemConfig.json"

settings = {}
responseVariables = {}
apiData = defaultdict(lambda: "")
messageQueue = []
bets = {
	"status": "waitForGame",
	"gamblers": set(),
	"bets": [],
	"totalGambled": 0,
	"apiCallDone": False,
	"latestApiUpdateTimestamp": time.time(),
	"totalGambledWin": 0,
	"totalGambledLose": 0,
	"updateRespondJoinedBetInterval": 3,
	"updateInterval": 2,
	"timeSinceLastViewerJoinedBet": 0,
	"timeSinceLastUpdate": time.time(),
	"recentlyJoinedUsers": [],
	"noBetsOnlyVotes": False,
	"duplicateNamesFound": False,
	"isPercentageBased": False
}
raceLongName = {
	"Z": "zerg",
	"T": "terran",
	"P": "protoss",
	"R": "random",
}

#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
	global responseVariables, settings, configFile
	path = os.path.dirname(__file__)

	try:
		themes = [x for x in os.listdir(os.path.join(path, "Overlays")) if os.path.isdir(os.path.join(path, "Overlays", x))]
		rewriteUiConfig(dictKey="overlayThemeNames", newItems=themes, configFile=os.path.join(path, "UI_Config.json"))

		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')

		if len(settings.get("overlayThemeNames", "")) != 0:
			settings["configFileLoaded"] = True
	except Exception as e:
		#Debug("Error: {}".format(e))
		return
	
	PushData("initThemeData")

	responseVariables = {
		"$mychannel": Parent.GetDisplayName(Parent.GetChannelName()),
		"$currencyName": Parent.GetCurrencyName(),
		"$cmdBetWin": settings["cmdBetWin"],
		"$cmdBetLose": settings["cmdBetLose"],
		"$cmdAbort": settings["cmdAbort"],
		"$rewardMultiplier": settings["rewardMultiplier"],
		"$minBet": settings["minBet"],
		"$maxBet": settings["maxBet"],
		"$fixedAmount": settings["fixedVotingAmount"],
	}
	# automatically fixes the issue of trailing whitespace
	# TODO: when users enter their character code, e.g. burny#1337
	settings["streamerUsernames"] = []
	settings["streamerUsernames"].append(settings["bnetUsername1"].lower().strip())
	settings["streamerUsernames"].append(settings["bnetUsername2"].lower().strip())
	settings["streamerUsernames"].append(settings["bnetUsername3"].lower().strip())
	settings["streamerUsernames"].append(settings["bnetUsername4"].lower().strip())
	settings["streamerUsernames"].append(settings["bnetUsername5"].lower().strip())
	bets["updateRespondJoinedBetInterval"] = int(settings["betUserCollectionTime"])

	responseVariables["$totalAmountGambled"] = 0
	responseVariables["$totalPointsWon"] = "0"
	responseVariables["$totalPointsLost"] = "0"
	responseVariables["$winnersNames"] = ""
	responseVariables["$winnersWithAmount"] = ""
	responseVariables["$losersNames"] = ""
	responseVariables["$losersWithAmount"] = ""
	responseVariables["$betDuration"] = str(int(settings["betDuration"]))
	responseVariables["$rewardMultiplier"] = str(settings["rewardMultiplier"])
	try:
		responseVariables["$minBet"] = str(int(settings["minBet"]))
	except ValueError:
		settings["minBet"] = 0
		responseVariables["$minBet"] = "0"
	try:
		responseVariables["$maxBet"] = str(int(settings["maxBet"]))
	except ValueError:
		settings["maxBet"] = 9999999999999
		responseVariables["$maxBet"] = "9999999999999"
	settings["betChoices"] = [settings["cmdBetWin"].lower(), settings["cmdBetLose"].lower()]
	return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
	Init()
	return

#---------------------------------------
# Communication with the Overlay
#---------------------------------------
def PushData(eventName):
	global responseVariables, bets, settings

	if eventName == "start":
		Parent.BroadcastWsEvent("EVENT_INIT_THEME", json.dumps({"themeName": settings["overlayThemeNames"]}, ensure_ascii=False))

		tempChatCmdWin = settings["overlayChatCmdWin"]
		tempChatCmdLose = settings["overlayChatCmdLose"]
		tempLblWin = settings["overlayLabelWin"]
		tempLblLose = settings["overlayLabelLose"]

		for variable, text in responseVariables.items():
			tempChatCmdWin = tempChatCmdWin.replace(variable, str(text))
			tempChatCmdLose = tempChatCmdLose.replace(variable, str(text))
			tempLblWin = tempLblWin.replace(variable, str(text))
			tempLblLose = tempLblLose.replace(variable, str(text))

		overlayDictionary = {
			"durationShowWinner": settings["overlayShowWinnerDuration"] * 1000,
			"hideAfterBetClosed": settings["overlayHideBetAfterClosed"],
			# "animationType": settings["overlayFadeInType"],
			"title": settings["overlayTitle"],
			"chatCmdWin": tempChatCmdWin[:20],
			"chatCmdLose": tempChatCmdLose[:20],
			"lblWin": tempLblWin[:24],
			"lblLose": tempLblLose[:24],
			"player1": responseVariables["$player1"][:15],
			"player2": responseVariables["$player2"][:15],
			"race1": raceLongName[responseVariables["$race1"]],
			"race2": raceLongName[responseVariables["$race2"]],
			"totalWin": str(int(bets["totalGambledWin"])),
			"totalLose": str(int(bets["totalGambledLose"])),
			"lblCurr": settings["overlayCurrencyShortName"][:8],
			"isPercentageBased": bets["isPercentageBased"],
			"themeName": settings["overlayThemeNames"],
			"showOverlay": settings["devShowOverlay"]
		}
		if bets["isPercentageBased"]: #set both percentages to 50% at the start of a new bet, instead of both 0%
			overlayDictionary["totalWin"] = "50"
			overlayDictionary["totalLose"] = "50"
			overlayDictionary["lblCurr"] = "%"
			overlayDictionary["isPercentageBased"] = bets["isPercentageBased"]
		if overlayDictionary["lblCurr"] == "":
			overlayDictionary["lblCurr"] = Parent.GetCurrencyName()

		Parent.BroadcastWsEvent("EVENT_BET_START", json.dumps(overlayDictionary, ensure_ascii=False))

	elif eventName == "end":
		Parent.BroadcastWsEvent("EVENT_BET_END", None)
	elif eventName == "update":
		if bets["isPercentageBased"]:
			totalTemp = max(1, int(bets["totalGambledWin"]) + int(bets["totalGambledLose"]))
			overlayDictionary = {
				"totalWin": round(100 * int(bets["totalGambledWin"]) / totalTemp),
				"totalLose": 100 - round(100 * int(bets["totalGambledWin"]) / totalTemp),
				"lblCurr": "%",
			}
		else:
			overlayDictionary = {
				"totalWin": int(bets["totalGambledWin"]),
				"totalLose": int(bets["totalGambledLose"]),
				"lblCurr": settings["overlayCurrencyShortName"][:8],
			}
		overlayDictionary["isPercentageBased"] = bets["isPercentageBased"]
		if overlayDictionary["lblCurr"] == "":
			overlayDictionary["lblCurr"] = Parent.GetCurrencyName()[:8]
		Parent.BroadcastWsEvent("EVENT_BET_UPDATE", json.dumps(overlayDictionary, ensure_ascii=False))

	elif eventName == "abort":
		Parent.BroadcastWsEvent("EVENT_BET_ABORT", None)
	elif eventName == "win":
		Parent.BroadcastWsEvent("EVENT_BET_WIN", None)
	elif eventName == "lose":
		Parent.BroadcastWsEvent("EVENT_BET_LOSE", None)
	elif eventName == "initThemeData":
		Parent.BroadcastWsEvent("EVENT_INIT_THEME", json.dumps({
			"themeName": settings["overlayThemeNames"]			
			}, ensure_ascii=False))
		if settings["devShowOverlay"]:
			Parent.BroadcastWsEvent("EVENT_BET_SHOW", None)
		pass
	return

#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	global settings, bets, responseVariables

	
	if settings.get("configFileLoaded", False):
		if data.IsChatMessage():
			responseVariables["$user"] = Parent.GetDisplayName(data.User)
			responseVariables["$points"] = str(Parent.GetPoints(data.User))

			if data.GetParamCount() == 1 and data.GetParam(0).lower() == settings["cmdAbort"]:
				if bets["status"] in ["open", "closed"] \
					and ((settings["allowModsToAbort"] and Parent.HasPermission(data.User, "Moderator", "")) \
					or Parent.HasPermission(data.User, "Caster", "")):

					refundBets()
					# for bet in bets["bets"]:
					# 	Parent.AddPoints(bet["username"], bet["betInvestment"])
					bets["bets"] = []
					bets["status"] = "waitForMenu"
					PushData("abort")
					SendMessage(settings["responseBetCanceled"])

			elif data.GetParamCount() >= 1 and data.GetParam(0).lower() in settings["betChoices"] and bets["status"] == "open":
				try:
					#this part is about the betting system, e.g. "#win 50"
					if not bets["noBetsOnlyVotes"]:
						if data.GetParamCount() >= 2:
							addGambler(data.User, int(data.GetParam(1)), data.GetParam(0))
							PushData("update")
						else:
							SendMessage(settings["responseHowToUseBetCommand"])

					else: #this part is about the voting system (when betting was changed to voting), e.g. "#win"
						if data.User in bets["gamblers"] and not settings["devAllowMultipleEntries"]:
							SendMessage(settings["responseUserAlreadyPlacedBet"])
						else:
							if bets["votingUsesCurrency"]:
								if Parent.GetPoints(data.User) >= bets["fixedVotingAmount"]:
									addGambler(data.User, bets["fixedVotingAmount"], data.GetParam(0), ignoreCheck=True)
									PushData("update")
								else:
									SendMessage(settings["responseNotEnoughPoints"])
							else:								
								addGambler(data.User, 0, data.GetParam(0), ignoreCheck=True)
								PushData("update")
				except ValueError:
					SendMessage(settings["responseHowToUseBetCommand"])
	return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	global apiData, settings, bets, responseVariables, messageQueue

	if settings.get("configFileLoaded", False):
		time1 = time.time()

		for item in messageQueue:
			if item["deliverTime"] < time1:
				SendMessage(item["message"])
				messageQueue.remove(item)
				break

		if time1 - bets["timeSinceLastViewerJoinedBet"] > bets["updateRespondJoinedBetInterval"] and len(bets["recentlyJoinedUsers"]) > 0:
			bets["timeSinceLastViewerJoinedBet"] = time1
			SendMessage(settings["responseUserJoinedBet"])
			bets["recentlyJoinedUsers"] = []

		if time1 - bets["timeSinceLastUpdate"] > bets["updateInterval"]:
			bets["timeSinceLastUpdate"] = time1
			if bets["apiCallDone"]:
				bets["apiCallDone"] = False
				# - "waitForGame" means the script waits for a new game to launch so it can open a new bet
				# - "open" means the betting is open and viewers are able to bet/vote
				# - "closed" means the game has gone past bets["betDuration"] and viewers can no longer gamble
				# - "abort" means "!abort" command was used or the game has ended before bets["betDuration"] has passed
				# - "waitForMenu" can have several reasons that make the script wait to until the streamer is back in sc2 menu
				
				if bets["status"] in ["waitForGame"]:
					if bets["duplicateNamesFound"] and apiData["inStarcraftLocation"] in ["1v1AsPlayer"]:
						# if duplicate names have been found, instantly close the bet system - no overlay will show up
						SendMessage(settings["responseTwoMatchingNames"])
						bets["status"] = "waitForMenu"	

					elif apiData["inStarcraftLocation"] in ["1v1AsPlayer"] and int(apiData["ingameSecs"]) < int(settings["betDuration"]):
						resetBetVariables()
						# bets["status"] = "open"
						SendMessage(settings["responseBetOpened"])
						PushData("start")
					else:
						# script gets here if streamer is in menu / replay / starcraft not running
						pass

				elif bets["status"] in ["waitForMenu"]:
					if apiData["inStarcraftLocation"] == "menu":
						bets["status"] = "waitForGame"
					else:
						# script gets here if streamer is in game but the bet was canceled (duplicate name, or #abort command)
						pass

				elif bets["status"] in ["open"]:					
					if int(apiData["ingameSecs"]) > int(settings["betDuration"]) and bets["status"] == "open":
						# closing the bet because the in-game time passed the betDuration
						bets["status"] = "closed"
						PushData("end")
						SendMessage(settings["responseBetClosed"])

					elif apiData["player1Result"] != "undecided" and apiData["inStarcraftLocation"] == "menu":
						# cancels the bets
						refundBets()
						bets["bets"] = []
						bets["status"] = "waitForGame"
						PushData("abort")
						SendMessage(settings["responseBetCanceled"])
					else:
						# shouldnt ever get here
						pass

				elif bets["status"] in ["closed"]:	
					if apiData["player1Result"] != "undecided" and apiData["inStarcraftLocation"] == "menu":
						# paying out the correct bets

						# set local variables
						totalPointsWon = 0
						totalPointsLost = 0
						userListCorrectGamble = []
						userListCorrectGambleWithAmount = []
						userListWrongGamble = []
						userListWrongGambleWithAmount = []

						betWinnerCommand = ""
						if apiData["player1Result"] == "victory":
							betWinnerCommand = bets["cmdBetWin"].lower()
							PushData("win")
						elif apiData["player1Result"] == "defeat":
							betWinnerCommand = bets["cmdBetLose"].lower()
							PushData("lose")

						# paying out viewers/betters who placed a bet or a vote (only if the vote-with-currency was on)

						# if not bets["noBetsOnlyVotes"] or (bets["noBetsOnlyVotes"] and bets["votingUsesCurrency"]):
						if True:
							# calculate the total correct/wrong bets and the amount the users won							
							userPointsWon = {bet["username"]: int(round(bets["rewardMultiplier"] * bet["betInvestment"])) for bet in bets["bets"] if bet["betChoice"] == betWinnerCommand}
							for correctGambler, amountWon in userPointsWon.items():
								Parent.AddPoints(correctGambler, amountWon)

							totalPointsWon = sum([userPointsWon[bet["username"]] for bet in bets["bets"] if bet["betChoice"] == betWinnerCommand])
							totalPointsLost = sum([bet["betInvestment"] for bet in bets["bets"] if bet["betChoice"] != betWinnerCommand])
							
							userListCorrectGamble = ["@" + bet["username"] for bet in bets["bets"] if bet["betChoice"] == betWinnerCommand]
							userListCorrectGambleWithAmount = ["@{} ({})".format(bet["username"], userPointsWon[bet["username"]]) for bet in bets["bets"] if bet["betChoice"] == betWinnerCommand]
							
							userListWrongGamble = ["@" + bet["username"] for bet in bets["bets"] if bet["betChoice"] != betWinnerCommand]
							userListWrongGambleWithAmount = ["@{} ({})".format(bet["username"], bet["betInvestment"]) for bet in bets["bets"] if bet["betChoice"] != betWinnerCommand]

							bets["bets"] = []
							responseVariables["$totalPointsWon"] = totalPointsWon
							responseVariables["$totalPointsLost"] = totalPointsLost
							responseVariables["$winnersNames"] = ", ".join(userListCorrectGamble)
							responseVariables["$winnersWithAmount"] = ", ".join(userListCorrectGambleWithAmount)
							responseVariables["$losersNames"] = ", ".join(userListWrongGamble)
							responseVariables["$losersWithAmount"] = ", ".join(userListWrongGambleWithAmount)
							messageDelay = settings["betWinnerAnnoucementDelay"]
							if apiData["player1Result"] == "victory":
								if bets["totalGambled"] == 0:
									SendMessage(settings["responseVictoryNoBets"], delayInSeconds=messageDelay)
								elif totalPointsWon == 0:
									SendMessage(settings["responseVictoryWrongBets"], delayInSeconds=messageDelay)
								else:
									SendMessage(settings["responseVictoryCorrectBets"], delayInSeconds=messageDelay)
							elif apiData["player1Result"] == "defeat":
								if bets["totalGambled"] == 0:
									SendMessage(settings["responseDefeatNoBets"], delayInSeconds=messageDelay)
								elif totalPointsWon == 0:
									SendMessage(settings["responseDefeatWrongBets"], delayInSeconds=messageDelay)
								else:
									SendMessage(settings["responseDefeatCorrectBets"], delayInSeconds=messageDelay)
						bets["status"] = "waitForGame"	
					else:
						# script goes here if streamer is in a game past bets["betDuration"] - so the script is basically waiting for the game to finish and streamer going back into menu
						pass			

			else:
				threading.Thread(target=GetSc2ApiResponse, args=()).start()
	return

##################
# HELPER FUNCTIONS
##################

# sends message to streamer's twitch channel with variables replaced by text
def SendMessage(string, delayInSeconds=0):
	global responseVariables, messageQueue
	for variable, text in responseVariables.items():
		if type(text) == type(0.1):
			string = string.replace(variable, str(int(text)))
		else:
			string = string.replace(variable, str(text))
	if delayInSeconds == 0:
		Parent.SendTwitchMessage(string[:490])
	else:
		messageQueue.append({
			"deliverTime": int(time.time()) + delayInSeconds,
			"message": string
		})

def GetSc2ApiResponse():
	global gameUrl, uiUrl, bets, settings
	try:
		gameResponse = json.loads(json.loads(Parent.GetRequest(gameUrl, {}))['response'])
		uiResponse = json.loads(json.loads(Parent.GetRequest(uiUrl, {}))['response'])
		time1 = time.time()
		if bets["latestApiUpdateTimestamp"] < time1:
			bets["latestApiUpdateTimestamp"] = time1
			if ProcessClientApiData(gameResponse, uiResponse):
				return True

	except Exception as e:
		print("Unknown error while attempting to get SC2API response", e)
		# Debug("Unknown error while attempting to get SC2API response: {}".format(e))
		if bets["status"] in ["open", "closed"]:
			bets["status"] = "waitForGame"
			refundBets()
			# for bet in bets["bets"]:
			# 	Parent.AddPoints(bet["username"], bet["betInvestment"])
			bets["bets"] = []
			SendMessage(settings["responseStarcraftClosed"])
	return False

def ProcessClientApiData(gameResponse, uiResponse):
	global apiData, bets, settings
	try:
		if len(gameResponse["players"]) == 2:
			apiData["player1Race"] = gameResponse["players"][0]["race"][0].upper()
			apiData["player2Race"] = gameResponse["players"][1]["race"][0].upper()
			apiData["player1Name"] = gameResponse["players"][0]["name"]
			apiData["player2Name"] = gameResponse["players"][1]["name"]
			apiData["player1Result"] = gameResponse["players"][0]["result"].lower()
			apiData["player2Result"] = gameResponse["players"][1]["result"].lower()
			apiData["ingameMins"] = str(int(gameResponse["displayTime"])//60)
			apiData["ingameSecs"] = str(int(gameResponse["displayTime"]))

			if apiData["player1Name"].lower() in settings["streamerUsernames"]:
				apiData["streamerIsInValid1v1Game"] = True
				if gameResponse["players"][1]["type"] == "computer":
					if not settings["devEnableVsAi"]:
						apiData["streamerIsInValid1v1Game"] = False
			elif apiData["player2Name"].lower() in settings["streamerUsernames"]:
				apiData["player1Race"], apiData["player2Race"] = apiData["player2Race"], apiData["player1Race"]
				apiData["player1Name"], apiData["player2Name"] = apiData["player2Name"], apiData["player1Name"]
				apiData["player1Result"], apiData["player2Result"] = apiData["player2Result"], apiData["player1Result"]
				apiData["streamerIsInValid1v1Game"] = True
				if gameResponse["players"][0]["type"] == "computer":
					if not settings["devEnableVsAi"]:
						apiData["streamerIsInValid1v1Game"] = False
			else:
				apiData["streamerIsInValid1v1Game"] = False
			# both names (streamer and his opponent) have a username that is in the list of usernames of the streamer (e.g. this can be the case when both have the same barcodes)
			if apiData["player1Name"].lower() in settings["streamerUsernames"] and apiData["player2Name"].lower() in settings["streamerUsernames"] :
				apiData["streamerIsInValid1v1Game"] = False
				bets["duplicateNamesFound"] = True
			else:
				bets["duplicateNamesFound"] = False
			matchup = apiData["player1Race"] + "v" + apiData["player2Race"]

			if apiData["streamerIsInValid1v1Game"]:
				responseVariables["$player1"] = apiData["player1Name"]
				responseVariables["$player2"] = apiData["player2Name"]
				responseVariables["$race1"] = apiData["player1Race"]
				responseVariables["$race2"] = apiData["player2Race"]

			# only change the location variable if duplicate names haven't been found
			# if not bets["duplicateNamesFound"]:
			if uiResponse["activeScreens"] == []:
				if len(gameResponse["players"]) == 2:
					if gameResponse["isReplay"]:
						apiData["inStarcraftLocation"] = "1v1Replay"
					else:
						if apiData["streamerIsInValid1v1Game"]:
							apiData["inStarcraftLocation"] = "1v1AsPlayer"
						else:
							apiData["inStarcraftLocation"] = "1v1AsCaster"
				else:
					apiData["inStarcraftLocation"] = "other"
			else:
				apiData["inStarcraftLocation"] = "menu"
			bets["apiCallDone"] = True
			return True

	except Exception as e:
		if bets["status"] in ["open", "closed"]:
			bets["status"] = "waitForGame"
			refundBets()
			# for bet in bets["bets"]:
			# 	Parent.AddPoints(bet["username"], bet["betInvestment"])
			bets["bets"] = []
			SendMessage(settings["responseStarcraftClosed"])
		print("Unknown error while attempting to collect data from SC2 API:", e)
	return False

##################
# betting related
##################

def resetBetVariables():
	global bets, responseVariables, settings
	bets["status"] = "open"
	bets["bets"] = []
	bets["gamblers"] = set()
	bets["recentlyJoinedUsers"] = []
	bets["totalGambled"] = 0
	bets["totalGambledWin"] = 0
	bets["totalGambledLose"] = 0
	responseVariables["$totalAmountGambled"] = 0
	responseVariables["$totalPointsWon"] = "0"
	responseVariables["$totalPointsLost"] = "0"
	responseVariables["$winnersNames"] = ""
	responseVariables["$winnersWithAmount"] = ""
	responseVariables["$losersNames"] = ""
	responseVariables["$losersWithAmount"] = ""
	# settings all these following variables to local variables in case the streamer changes the variables while a game is running
	bets["noBetsOnlyVotes"] = settings["noBetsOnlyVotes"]
	bets["isPercentageBased"] = settings["isPercentageBased"]
	bets["votingUsesCurrency"] = settings["votingUsesCurrency"]
	bets["fixedVotingAmount"] = settings["fixedVotingAmount"]
	bets["cmdBetWin"] = settings["cmdBetWin"]
	bets["cmdBetLose"] = settings["cmdBetLose"]
	bets["rewardMultiplier"] = settings["rewardMultiplier"]

def payoutCorrectBets():
	pass

def gamblerAllowedToJoin(username, investmentAmount):
	global bets
	if Parent.GetPoints(username) < investmentAmount:
		SendMessage(settings["responseNotEnoughPoints"])
		return False
	if username in bets["gamblers"] and not settings["devAllowMultipleEntries"]:
		SendMessage(settings["responseUserAlreadyPlacedBet"])
		return False
	if investmentAmount < int(settings["minBet"]) or investmentAmount > int(settings["maxBet"]):
		SendMessage(settings["responseNotCorrectBetAmount"])
		return False
	return True

def addGambler(username, investmentAmount, betChoice, ignoreCheck=False):
	global bets, settings, responseVariables
	if ignoreCheck or gamblerAllowedToJoin(username, investmentAmount):
		bets["bets"].append({"username": username, "betChoice": betChoice.lower(), "betInvestment": investmentAmount})
		Parent.RemovePoints(username, investmentAmount)
		bets["gamblers"].add(username)
		bets["recentlyJoinedUsers"].append("@" + Parent.GetDisplayName(username))
		responseVariables["$recentlyJoinedUsers"] = ", ".join(bets["recentlyJoinedUsers"])
		bets["timeSinceLastViewerJoinedBet"] = time.time()
		bets["totalGambled"] += investmentAmount
		responseVariables["$totalAmountGambled"] = str(bets["totalGambled"])
		if betChoice.lower() == bets["cmdBetWin"].lower():
			bets["totalGambledWin"] += investmentAmount
		else:
			bets["totalGambledLose"] += investmentAmount

def refundBets():
	global bets
	for bet in bets["bets"]: # paying back viewers who already placed a bet if the game ended before "betDuration" ran out or when the abort command was used
		Parent.AddPoints(bet["username"], bet["betInvestment"])
	pass

# writes new themes to the UI_Config.json
def rewriteUiConfig(dictKey, newItems, configFile=""):
	dictionary = OrderedDict()
	oldItems = []
	with codecs.open(configFile, encoding='utf-8-sig', mode='r') as file:
		dictionary = json.load(file, encoding='utf-8-sig', object_pairs_hook=OrderedDict)
		oldItems = dictionary[dictKey]["items"]
		dictionary[dictKey]["items"] = newItems
		if len(dictionary[dictKey]["items"]) > 0:
			dictionary[dictKey]["value"] = dictionary[dictKey]["value"] if dictionary[dictKey]["value"] in dictionary[dictKey]["items"] else dictionary[dictKey]["items"][0]
	
	if dictionary != OrderedDict() and sorted(oldItems) != sorted(newItems):
		with codecs.open(configFile, encoding='utf-8-sig', mode='w') as file:
			json.dump(dictionary, file, encoding='utf-8-sig', indent=4, sort_keys=False)
			# Debug("Successfully rewritten ui config file")

def TestOverlay():
	global bets, settings, responseVariables
	if settings.get("configFileLoaded", False):
		if not bets.get("TestOverlayActive", False):
			bets["TestOverlayActive"] = True
			threading.Thread(target=TestOverlayThread, args=()).start()

def TestOverlayThread():
	global bets, settings, responseVariables

	sleepTime = 5

	Parent.BroadcastWsEvent("EVENT_INIT_THEME", json.dumps({"themeName": settings["overlayThemeNames"]}, ensure_ascii=False))

	tempChatCmdWin = settings["overlayChatCmdWin"]
	tempChatCmdLose = settings["overlayChatCmdLose"]
	tempLblWin = settings["overlayLabelWin"]
	tempLblLose = settings["overlayLabelLose"]

	for variable, text in responseVariables.items():
		tempChatCmdWin = tempChatCmdWin.replace(variable, str(text))
		tempChatCmdLose = tempChatCmdLose.replace(variable, str(text))
		tempLblWin = tempLblWin.replace(variable, str(text))
		tempLblLose = tempLblLose.replace(variable, str(text))

	overlayDictionary = {
		"durationShowWinner": settings["overlayShowWinnerDuration"] * 1000,
		"hideAfterBetClosed": settings["overlayHideBetAfterClosed"],
		"title": settings["overlayTitle"],
		"chatCmdWin": tempChatCmdWin[:20],
		"chatCmdLose": tempChatCmdLose[:20],
		"lblWin": tempLblWin[:24],
		"lblLose": tempLblLose[:24],
		"player1": "BrainLangerNameeee"[:15],
		"player2": "Burny"[:15],
		"race1": "zerg",
		"race2": "zerg",
		"totalWin": "0",
		"totalLose": "0",
		"lblCurr": settings["overlayCurrencyShortName"][:8],
		"isPercentageBased": settings["isPercentageBased"],
		"themeName": settings["overlayThemeNames"],
		"showOverlay": settings["devShowOverlay"]
	}
	if settings["isPercentageBased"]:
		overlayDictionary["totalWin"] = "50"
		overlayDictionary["totalLose"] = "50"
		overlayDictionary["lblCurr"] = "%"
		overlayDictionary["isPercentageBased"] = settings["isPercentageBased"]
	if overlayDictionary["lblCurr"] == "":
		overlayDictionary["lblCurr"] = Parent.GetCurrencyName()

	Parent.BroadcastWsEvent("EVENT_BET_START", json.dumps(overlayDictionary, ensure_ascii=False))


	time.sleep(sleepTime)
	# UPDATE - LOSE 
	if settings["isPercentageBased"]:
		overlayDictionary = {
			"totalWin": 0,
			"totalLose": 100,
			"lblCurr": "%",
		}
	else:
		overlayDictionary = {
			"totalWin": 0,
			"totalLose": 69,
			"lblCurr": settings["overlayCurrencyShortName"][:8],
		}
	overlayDictionary["isPercentageBased"] = settings["isPercentageBased"]
	if overlayDictionary["lblCurr"] == "":
		overlayDictionary["lblCurr"] = Parent.GetCurrencyName()[:8]
	Parent.BroadcastWsEvent("EVENT_BET_UPDATE", json.dumps(overlayDictionary, ensure_ascii=False))


	time.sleep(sleepTime)
	# UPDATE - WIN 

	if settings["isPercentageBased"]:
		overlayDictionary.update({
			"totalWin": 69,
			"totalLose": 31
		})
	else:
		overlayDictionary.update({
			"totalWin": 420
		})
	Parent.BroadcastWsEvent("EVENT_BET_UPDATE", json.dumps(overlayDictionary, ensure_ascii=False))
	
	time.sleep(sleepTime)
	# Bet Closed (Hide Bet if option enabled)
	Parent.BroadcastWsEvent("EVENT_BET_END", None)

	time.sleep(sleepTime)
	# WINNER SHOWN
	Parent.BroadcastWsEvent("EVENT_BET_WIN", None)
	# BET OVER

	bets["TestOverlayActive"] = False

def Debug(message):
	if debuggingMode:
		Parent.Log("Betting", message)

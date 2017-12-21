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
Version = "1.1.3"

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
bets = {
	"status": "reset",
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
	with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
		settings = json.load(file, encoding='utf-8-sig')

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
			"animationType": settings["overlayFadeInType"],
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
			"isPercentageBased": bets["isPercentageBased"]
		}
		if bets["isPercentageBased"]: #set both percentages to 50% at the start of a new bet, instead of both 0%
			overlayDictionary["totalWin"] = "50"
			overlayDictionary["totalLose"] = "50"
			overlayDictionary["lblCurr"] = "%"
			overlayDictionary["isPercentageBased"] = bets["isPercentageBased"]
		if overlayDictionary["lblCurr"] == "":
			overlayDictionary["lblCurr"] = Parent.GetCurrencyName()[:8]

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
	return

#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	global settings, bets, responseVariables

	if data.IsChatMessage():
		responseVariables["$user"] = Parent.GetDisplayName(data.User)
		responseVariables["$points"] = str(Parent.GetPoints(data.User))

		if data.GetParamCount() == 1 and data.GetParam(0).lower() == settings["cmdAbort"]:
			if settings["allowModsToAbort"] and Parent.HasPermission(data.User, "Moderator", ""):
				for bet in bets["bets"]:
					Parent.AddPoints(bet["username"], bet["betInvestment"])
				bets["bets"] = []
				bets["status"] = "abort"
				PushData("abort")
				SendMessage(settings["responseBetCanceled"])
			elif Parent.HasPermission(data.User, "Caster", ""):
				for bet in bets["bets"]:
					Parent.AddPoints(bet["username"], bet["betInvestment"])
				bets["bets"] = []
				bets["status"] = "abort"
				PushData("abort")
				SendMessage(settings["responseBetCanceled"])

		elif data.GetParamCount() >= 1 and data.GetParam(0).lower() in settings["betChoices"] and bets["status"] == "open":
			try:
				#this part is about the betting system, e.g. "#win 50"
				if False == bets["noBetsOnlyVotes"]:
					if Parent.GetPoints(data.User) >= int(data.GetParam(1)):
						if int(settings["minBet"]) <= int(data.GetParam(1)) <= int(settings["maxBet"]):
							if data.User in bets["gamblers"] and not settings["devAllowMultipleEntries"]:
								SendMessage(settings["responseUserAlreadyPlacedBet"])
							else:
								bets["bets"].append({"username": data.User, "betChoice": data.GetParam(0).lower(), "betInvestment": int(data.GetParam(1))})
								Parent.RemovePoints(data.User, int(data.GetParam(1)))
								bets["gamblers"].add(data.User)
								bets["recentlyJoinedUsers"].append("@" + Parent.GetDisplayName(data.User))
								responseVariables["$recentlyJoinedUsers"] = ", ".join(bets["recentlyJoinedUsers"])
								bets["timeSinceLastViewerJoinedBet"] = time.time()
								bets["totalGambled"] += int(data.GetParam(1))
								responseVariables["$totalAmountGambled"] = str(bets["totalGambled"])
								if data.GetParam(0).lower() == bets["cmdBetWin"].lower():
									bets["totalGambledWin"] += int(data.GetParam(1))
								else:
									bets["totalGambledLose"] += int(data.GetParam(1))
								PushData("update")
						else:
							SendMessage(settings["responseNotCorrectBetAmount"])
					else:
						SendMessage(settings["responseNotEnoughPoints"])

				else: #this part is about the voting system (when betting was changed to voting)
					if data.User in bets["gamblers"] and not settings["devAllowMultipleEntries"]:
						SendMessage(settings["responseUserAlreadyPlacedBet"])
					else:
						if bets["votingUsesCurrency"]:
							if Parent.GetPoints(data.User) >= bets["fixedVotingAmount"]:
								bets["bets"].append({"username": data.User, "betChoice": data.GetParam(0).lower(), "betInvestment": bets["fixedVotingAmount"]})
								Parent.RemovePoints(data.User, bets["fixedVotingAmount"])
								bets["gamblers"].add(data.User)
								bets["recentlyJoinedUsers"].append("@" + Parent.GetDisplayName(data.User))
								responseVariables["$recentlyJoinedUsers"] = ", ".join(bets["recentlyJoinedUsers"])
								bets["timeSinceLastViewerJoinedBet"] = time.time()
								bets["totalGambled"] += bets["fixedVotingAmount"]
								responseVariables["$totalAmountGambled"] = str(bets["totalGambled"])
								if data.GetParam(0).lower() == bets["cmdBetWin"].lower():
									bets["totalGambledWin"] += bets["fixedVotingAmount"]
								else:
									bets["totalGambledLose"] += bets["fixedVotingAmount"]
								PushData("update")
							else:
								SendMessage(settings["responseNotEnoughPoints"])
						else:
							bets["recentlyJoinedUsers"].append("@" + Parent.GetDisplayName(data.User))
							bets["timeSinceLastViewerJoinedBet"] = time.time()
							responseVariables["$recentlyJoinedUsers"] = ", ".join(bets["recentlyJoinedUsers"])
							if data.GetParam(0).lower() == bets["cmdBetWin"].lower():
								bets["totalGambledWin"] += 1
							else:
								bets["totalGambledLose"] += 1
							bets["gamblers"].add(data.User)
							PushData("update")
			except ValueError:
				SendMessage(settings["responseHowToUseBetCommand"])
	return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	global apiData, settings, bets, responseVariables

	time1 = time.time()
	if time1 - bets["timeSinceLastViewerJoinedBet"] > bets["updateRespondJoinedBetInterval"] and len(bets["recentlyJoinedUsers"]) > 0:
		bets["timeSinceLastViewerJoinedBet"] = time1
		SendMessage(settings["responseUserJoinedBet"])
		bets["recentlyJoinedUsers"] = []

	if time1 - bets["timeSinceLastUpdate"] > bets["updateInterval"]:
		bets["timeSinceLastUpdate"] = time1
		if bets["apiCallDone"]:
			bets["apiCallDone"] = False

			# this "if" triggers when two names were found, then it sends the script into a status="duplicateNamesFound" and stays there until the streamers goes back to the menu
			if bets["duplicateNamesFound"] and bets["status"] == "reset" and apiData["inStarcraftLocation"] in ["1v1AsPlayer", "1v1AsCaster", "1v1Replay"]:
				# if duplicate names have been found, instantly close the bet system - no overlay will show up
				# SendMessage("Loc: {}, P1: {}, P2: {}, duplicate: {}".format(apiData["inStarcraftLocation"], apiData["player1Name"].lower(), apiData["player2Name"].lower(), bets["duplicateNamesFound"]))
				SendMessage(settings["responseTwoMatchingNames"])
				bets["status"] = "duplicateNamesFound"

			elif apiData["inStarcraftLocation"] == "1v1AsPlayer" and int(apiData["ingameSecs"]) < 30 and bets["status"] == "reset":
				# resetting all local variables to default values and preparing for a new game, might have to put this into a function instead
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
				SendMessage(settings["responseBetOpened"])
				PushData("start")

			elif int(apiData["ingameSecs"]) > int(settings["betDuration"]) and bets["status"] == "open":
				# closing the bet because the in-game time passed the betDuration
				bets["status"] = "closed"
				PushData("end")
				SendMessage(settings["responseBetClosed"])

			elif apiData["player1Result"] != "undecided" and bets["status"] in ["closed", "open", "abort", "duplicateNamesFound"] and apiData["inStarcraftLocation"] == "menu":	

				if bets["status"] == "duplicateNamesFound":
					# if previously both player names are in the list of usernames same as the streamer, no bets will be paid out and the script returns to its starting state
					bets["status"] = "reset"
					bets["duplicateNamesFound"] = False
					
				elif int(apiData["ingameSecs"]) < int(settings["betDuration"]) or bets["status"] == "abort":
					# cancels the bets
					for bet in bets["bets"]: # paying back viewers who already placed a bet if the game ended before "betDuration" ran out or when the abort command was used
						Parent.AddPoints(bet["username"], bet["betInvestment"])
					bets["bets"] = []
					bets["status"] = "reset"
					PushData("abort")
					SendMessage(settings["responseBetCanceled"])

				elif bets["status"] != "abort":
					# paying out the correct bets
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
					if (not bets["noBetsOnlyVotes"]) or (bets["noBetsOnlyVotes"] and bets["votingUsesCurrency"]):
						for bet in bets["bets"]:
							if bet["betChoice"] == betWinnerCommand:
								userPointsWon = int(round(bets["rewardMultiplier"] * bet["betInvestment"]))
								Parent.AddPoints(bet["username"], userPointsWon)
								totalPointsWon += userPointsWon
								if "@" + bet["username"] not in userListCorrectGamble:
									userListCorrectGamble.append("@" + bet["username"])
									userListCorrectGambleWithAmount.append("@" + bet["username"] + " (" + str(userPointsWon) +")")
							else:
								totalPointsLost += bet["betInvestment"]
								if "@" + bet["username"] not in userListWrongGamble:
									userListWrongGamble.append("@" + bet["username"])
									userListWrongGambleWithAmount.append("@" + bet["username"] + " (" + str(bet["betInvestment"]) +")")

						bets["bets"] = []
						responseVariables["$totalPointsWon"] = totalPointsWon
						responseVariables["$totalPointsLost"] = totalPointsLost
						responseVariables["$winnersNames"] = ", ".join(userListCorrectGamble)
						responseVariables["$winnersWithAmount"] = ", ".join(userListCorrectGambleWithAmount)
						responseVariables["$losersNames"] = ", ".join(userListWrongGamble)
						responseVariables["$losersWithAmount"] = ", ".join(userListWrongGambleWithAmount)
						if apiData["player1Result"] == "victory":
							if bets["totalGambled"] == 0:
								SendMessage(settings["responseVictoryNoBets"])
							elif totalPointsWon == 0:
								SendMessage(settings["responseVictoryWrongBets"])
							else:
								SendMessage(settings["responseVictoryCorrectBets"])
						elif apiData["player1Result"] == "defeat":
							if bets["totalGambled"] == 0:
								SendMessage(settings["responseDefeatNoBets"])
							elif totalPointsWon == 0:
								SendMessage(settings["responseDefeatWrongBets"])
							else:
								SendMessage(settings["responseDefeatCorrectBets"])
				bets["status"] = "reset"
		else:
			threading.Thread(target=GetSc2ApiResponse, args=()).start()
	return

def SendMessage(string):
	global responseVariables
	for variable, text in responseVariables.items():
		if type(text) == type(0.1):
			string = string.replace(variable, str(int(text)))
		else:
			string = string.replace(variable, str(text))
	Parent.SendTwitchMessage(string[:490])

def GetSc2ApiResponse():
	global gameUrl, uiUrl
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
	return False

def ProcessClientApiData(gameResponse, uiResponse):
	global apiData, bets
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
		if bets["status"] != "reset":
			bets["status"] = "reset"
			for bet in bets["bets"]:
				Parent.AddPoints(bet["username"], bet["betInvestment"])
			bets["bets"] = []
			SendMessage(settings["responseStarcraftClosed"])
		print("Unknown error while attempting to collect data from SC2 API:", e)
	return False

def Debug(message):
	if debuggingMode:
		Parent.Log("Betting", message)
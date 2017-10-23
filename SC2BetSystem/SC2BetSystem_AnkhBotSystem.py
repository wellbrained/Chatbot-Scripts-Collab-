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
import urllib2

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "SCII - Betting System"
Website = "https://www.brains-world.eu"
Description = "Automatic Betting System for StarCraft II"
Creator = "Brain & Burny"
Version = "1.1.1"

#---------------------------------------
#	Set Variables
#---------------------------------------
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
	with open(os.path.join(path, configFile)) as file:
		settings = json.load(file)

	responseVariables = {
		"$mychannel": Parent.GetChannelName(),
		"$currencyName": Parent.GetCurrencyName(),
		"$cmdBetWin": settings["cmdBetWin"],
		"$cmdBetLose": settings["cmdBetLose"],
		"$cmdAbort": settings["cmdAbort"],
		"$rewardMultiplier": settings["rewardMultiplier"],
		"$minBet": settings["minBet"],
		"$maxBet": settings["maxBet"],
	}
	settings["streamerUsernames"] = []
	settings["streamerUsernames"].append(settings["bnetUsername1"].lower())
	settings["streamerUsernames"].append(settings["bnetUsername2"].lower())
	settings["streamerUsernames"].append(settings["bnetUsername3"].lower())
	settings["streamerUsernames"].append(settings["bnetUsername4"].lower())
	settings["streamerUsernames"].append(settings["bnetUsername5"].lower())

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
		}
		Parent.BroadcastWsEvent("EVENT_BET_START", json.dumps(overlayDictionary))
	elif eventName == "end":
		Parent.BroadcastWsEvent("EVENT_BET_END", None)
	elif eventName == "update":
		overlayDictionary = {
			"totalWin": str(int(bets["totalGambledWin"])),
			"totalLose": str(int(bets["totalGambledLose"])),
			"lblCurr": settings["overlayCurrencyShortName"][:8],
		}
		Parent.BroadcastWsEvent("EVENT_BET_UPDATE", json.dumps(overlayDictionary))
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

	if settings["isEnabled"] and data.IsChatMessage():
		responseVariables["$user"] = data.User
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

		elif data.GetParamCount() == 2 and data.GetParam(0).lower() in settings["betChoices"] and bets["status"] == "open":
			try:
				if Parent.GetPoints(data.User) >= int(data.GetParam(1)):
					if int(settings["minBet"]) <= int(data.GetParam(1)) <= int(settings["maxBet"]):
						if data.User in bets["gamblers"]:
							SendMessage(settings["responseUserAlreadyPlacedBet"])
						else:
							bets["bets"].append({"username": data.User, "betChoice": data.GetParam(0).lower(), "betInvestment": int(data.GetParam(1))})
							Parent.RemovePoints(data.User, int(data.GetParam(1)))
							bets["gamblers"].add(data.User)
							bets["recentlyJoinedUsers"].append("@" + data.User)
							responseVariables["$recentlyJoinedUsers"] = ", ".join(bets["recentlyJoinedUsers"])
							bets["timeSinceLastViewerJoinedBet"] = time.time()
							bets["totalGambled"] += int(data.GetParam(1))
							responseVariables["$totalAmountGambled"] = str(bets["totalGambled"])
							if data.GetParam(0).lower() == settings["cmdBetWin"]:
								bets["totalGambledWin"] += int(data.GetParam(1))
							else:
								bets["totalGambledLose"] += int(data.GetParam(1))
							PushData("update")
					else:
						SendMessage(settings["responseNotCorrectBetAmount"])
				else:
					SendMessage(settings["responseNotEnoughPoints"])
			except ValueError:
				SendMessage(settings["responseHowToUseBetCommand"])
	return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	global apiData, settings, bets, responseVariables

	if settings["isEnabled"]:
		time1 = time.time()
		if time1 - bets["timeSinceLastViewerJoinedBet"] > bets["updateRespondJoinedBetInterval"] and len(bets["recentlyJoinedUsers"]) > 0:
			bets["timeSinceLastViewerJoinedBet"] = time1
			SendMessage(settings["responseUserJoinedBet"])
			bets["recentlyJoinedUsers"] = []

		if time1 - bets["timeSinceLastUpdate"] > bets["updateInterval"]:
			bets["timeSinceLastUpdate"] = time1
			if bets["apiCallDone"]:
				bets["apiCallDone"] = False
				if apiData["inStarcraftLocation"] == "1v1AsPlayer" and int(apiData["ingameSecs"]) < 30 and bets["status"] == "reset":
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
					PushData("start")
					SendMessage(settings["responseBetOpened"])

				elif int(apiData["ingameSecs"]) > int(settings["betDuration"]) and bets["status"] == "open":
					bets["status"] = "closed"
					PushData("end")
					SendMessage(settings["responseBetClosed"])

				elif apiData["player1Result"] != "undecided" and bets["status"] in ["closed", "open", "abort"]:
					if int(apiData["ingameSecs"]) < int(settings["betDuration"]):
						for bet in bets["bets"]:
							Parent.AddPoints(bet["username"], bet["betInvestment"])
						bets["bets"] = []
						bets["status"] = "reset"
						PushData("abort")
						SendMessage(settings["responseBetCanceled"])

					elif bets["status"] != "abort":
						totalPointsWon = 0
						totalPointsLost = 0
						userListCorrectGamble = []
						userListCorrectGambleWithAmount = []
						userListWrongGamble = []
						userListWrongGambleWithAmount = []

						betWinnerCommand = ""
						if apiData["player1Result"] == "victory":
							betWinnerCommand = settings["cmdBetWin"].lower()
							PushData("win")
						elif apiData["player1Result"] == "defeat":
							betWinnerCommand = settings["cmdBetLose"].lower()
							PushData("lose")

						for bet in bets["bets"]:
							if bet["betChoice"] == betWinnerCommand:
								userPointsWon = int(round(settings["rewardMultiplier"] * bet["betInvestment"]))
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
		gameResponse = json.load(urllib2.urlopen(gameUrl))
		uiResponse = json.load(urllib2.urlopen(uiUrl))
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
					apiData["streamerIsInValid1v1Game"] = False
			elif apiData["player2Name"].lower() in settings["streamerUsernames"]:
				apiData["player1Race"], apiData["player2Race"] = apiData["player2Race"], apiData["player1Race"]
				apiData["player1Name"], apiData["player2Name"] = apiData["player2Name"], apiData["player1Name"]
				apiData["player1Result"], apiData["player2Result"] = apiData["player2Result"], apiData["player1Result"]
				apiData["streamerIsInValid1v1Game"] = True
				if gameResponse["players"][0]["type"] == "computer":
					apiData["streamerIsInValid1v1Game"] = False
			else:
				apiData["streamerIsInValid1v1Game"] = False
			if apiData["player1Name"].lower() in settings["streamerUsernames"] and apiData["player2Name"].lower() in settings["streamerUsernames"] :
				apiData["streamerIsInValid1v1Game"] = False
				SendMessage(settings["responseTwoMatchingNames"])
			matchup = apiData["player1Race"] + "v" + apiData["player2Race"]

			if apiData["streamerIsInValid1v1Game"]:
				responseVariables["$player1"] = apiData["player1Name"]
				responseVariables["$player2"] = apiData["player2Name"]
				responseVariables["$race1"] = apiData["player1Race"]
				responseVariables["$race2"] = apiData["player2Race"]

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

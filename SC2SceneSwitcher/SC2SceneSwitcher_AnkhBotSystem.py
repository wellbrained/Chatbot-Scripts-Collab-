#---------------------------------------
#	Import Libraries
#---------------------------------------
import sys
import datetime
import json
import os
import clr
import urllib2

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "SCII - Scene Switcher"
Website = "https://www.brains-world.eu"
Description = "Scene Switcher for StarCraft II"
Creator = "Brain & Burny"
Version = "1.0.0"

#---------------------------------------
#	Set Variables
#---------------------------------------
gameUrl = "http://localhost:6119/game"
uiUrl = "http://localhost:6119/ui"
configFile = "SC2SceneSwitcherConfig.json"
settings = {}
currentScene = ""
lastSetScene = ""


#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
	global responseVariables, settings, configFile
	path = os.path.dirname(__file__)
	with open(os.path.join(path, configFile)) as file:
		settings = json.load(file)
	return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
	Init()
	return

#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	global settings, uiUrl, currentScene, lastSetScene

	if settings["isEnabled"]:
		try:
			uiResponse = json.load(urllib2.urlopen(uiUrl))

			if settings["isCasterModeEnabled"]:
				if uiResponse["activeScreens"] == []:
					currentScene = settings["obsSceneCasterInGame"]
				else:					
					currentScene = settings["obsSceneCasterInMenu"]
			else:
				if uiResponse["activeScreens"] == []:
					currentScene = settings["obsSceneInGame"]
				else:
					currentScene = settings["obsSceneInMenu"]

			if currentScene != "" and currentScene != lastSetScene:
				lastSetScene = currentScene
				Parent.SetOBSCurrentScene(currentScene)

		except requests.exceptions.ConnectionError:
			print("StarCraft 2 not running!")
		except ValueError:
			print("StarCraft 2 starting.")
		except Exception as e:
			print("Unknown error while attempting to get SC2API response", e)
	return
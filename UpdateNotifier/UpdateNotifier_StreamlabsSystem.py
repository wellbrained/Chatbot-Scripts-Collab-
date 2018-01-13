#---------------------------------------
#	Import Libraries
#---------------------------------------
import clr
import sys
import json
import os
import random
import ctypes
import codecs
import re

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "Update Notifier"
Website = "http://www.brains-world.eu"
Description = "Notifies you about updates on your installed scripts"
Creator = "Brain"
Version = "1.0.1"

#---------------------------------------
#	Set Variables
#---------------------------------------
configFile = "settings.json"
settings = {
	"successfullyLoaded": False
}
scripts = {}
toggleState = False

#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
	global settings, configFile
	# load settings.json file
	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
		settings["successfullyLoaded"] = True
	except:
		settings = {
			"cbShowInLog": True,
			"cbSendAsWhisper": False,
			"cbWriteInLogfile": False,
			"cbSendAsChatMsg": False,
			"cbSendAsWhisper": False,
			"cbNotifyOnSuccess": True,
		}

	return

def OpenReadMe():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)
    return

def OpenLogfile():
    """Open the Logfile.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "Logfile.txt")
    os.startfile(location)
    return

def CheckScripts():
	ScriptToggled(toggleState)
	return

def ScriptToggled(state):
	global settings, scripts, toggleState
	toggleState = state

	if state:
		# Get the '\Scripts' folder
		dirScripts = os.path.abspath(os.path.join(__file__, "../.."))
		# Regex for ScriptName, Version and Website
		compiledScriptName = re.compile("""((ScriptName)(\s)*(=)(\s)*(["'])(.)+(["']))""")
		compiledVersion = re.compile("""((Version)(\s)*(=)(\s)*(["'])([0-9a-zA-Z\.])+(["']))""")
		compiledWebsite = re.compile("""((Website)(\s)*(=)(\s)*(["'])(.)+(["']))""")

		# Cycle through the directory
		for subdir, dirs, files in os.walk(dirScripts):
			for file in files:
				filepath = os.path.join(subdir, file)

				# Iterate through SL files and get infos
				if filepath.endswith("_StreamlabsSystem.py") or filepath.endswith("_StreamlabsParameter.py"):
					with open(filepath) as inf:
						fileText = inf.read()
						
						foundName = [x[0] for x in compiledScriptName.findall(fileText)]
						foundVersion = [x[0] for x in compiledVersion.findall(fileText)]
						foundWebsite = [x[0] for x in compiledWebsite.findall(fileText)]
						
						if len(foundName) > 0 and len(foundVersion) > 0 and len(foundWebsite) > 0:
							scriptName = foundName[0].split("=")[1].strip().strip("\"").strip("\'")
							scriptVersion = foundVersion[0].split("=")[1].strip().strip("\"").strip("\'")
							scriptWebsite = foundWebsite[0].split("=")[1].strip().strip("\"").strip("\'")
							scripts[scriptName] = {
								"Name": scriptName,
								"Version": scriptVersion,
								"Website": scriptWebsite,
							}

		with codecs.open(os.path.join(os.path.dirname(__file__), "scriptInfos.json"), encoding='utf-8-sig', mode='w+') as file:
			json.dump(scripts, file, indent=4, sort_keys=True)

		CompareScripts()
	return

def CompareScripts():
	clientScripts = scripts
	response = json.loads(Parent.GetRequest("http://brains-world.eu/chatbot/serverInfo.json", {}))
	if response["status"] == 200:
		serverScripts = json.loads(response["response"])

		newScriptsAvailable = []
		for scriptName, scriptInfo in clientScripts.items():
			if scriptName in serverScripts:
				if scriptInfo["Version"] != serverScripts[scriptName]["Version"]: # 1.9.0 < 1.10.0
					newScriptsAvailable.append({
						"Name": scriptName,
						"ClientVersion": scriptInfo["Version"],
						"ServerVersion": serverScripts[scriptName]["Version"],
						"Website": serverScripts[scriptName]["Website"] if serverScripts[scriptName]["Website"] != "" else scriptInfo["Website"]
					})
		if len(newScriptsAvailable) > 0:
			notifyStringFormat = "{} {} (Server: {} -- {} )"

			# To Log
			if settings["cbShowInLog"]:
				notifyString = "\n".join([notifyStringFormat.format(x["Name"], x["ClientVersion"], x["ServerVersion"], x["Website"]) for x in newScriptsAvailable])
				Parent.Log("Update Notifier", "Different versions found: \n" + notifyString )

			# To Logfile.txt
			if settings["cbWriteInLogfile"]:
				notifyString = "\n".join([notifyStringFormat.format(x["Name"], x["ClientVersion"], x["ServerVersion"], x["Website"]) for x in newScriptsAvailable])
				with codecs.open(os.path.join(os.path.dirname(__file__), "Logfile.txt"), encoding='utf-8-sig', mode='w+') as file:
					file.write("Different versions found: \n" + notifyString)

			# To Twitch Chat
			if settings["cbSendAsChatMsg"]:
				notifyString = ", ".join([notifyStringFormat.format(x["Name"], x["ClientVersion"], x["ServerVersion"], x["Website"]) for x in newScriptsAvailable])
				Parent.SendTwitchMessage("Update Notifier found not up to date scripts: " + notifyString)
			
			# To Twitch Whisper
			if settings["cbSendAsWhisper"]:
				notifyString = ", ".join([notifyStringFormat.format(x["Name"], x["ClientVersion"], x["ServerVersion"], x["Website"]) for x in newScriptsAvailable])
				Parent.SendTwitchWhisper(Parent.GetChannelName(), "Update Notifier found not up to date scripts: " + notifyString)

		elif len(newScriptsAvailable) == 0 and settings["cbNotifyOnSuccess"]:
			# To Log
			if settings["cbShowInLog"]:
				Parent.Log("Update Notifier", "All scripts up to date!" )

			# To Logfile.txt
			if settings["cbWriteInLogfile"]:
				notifyString = "\n".join([notifyStringFormat.format(x["Name"], x["ClientVersion"], x["ServerVersion"], x["Website"]) for x in newScriptsAvailable])
				with codecs.open(os.path.join(os.path.dirname(__file__), "Logfile.txt"), encoding='utf-8-sig', mode='w+') as file:
					file.write("Update Notifier: All scripts up to date!")

			# To Twitch Chat
			if settings["cbSendAsChatMsg"]:
				Parent.SendTwitchMessage("Update Notifier: All scripts up to date!")
			
			# To Twitch Whisper
			if settings["cbSendAsWhisper"]:
				Parent.SendTwitchWhisper(Parent.GetChannelName(), "Update Notifier: All scripts up to date!")
	return

#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	global settings
	return
#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
	return
#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	return

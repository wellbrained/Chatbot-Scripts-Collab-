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
import clr
import codecs
import threading

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
ScriptName = "SCII - Scene Switcher"
Website = "https://www.brains-world.eu"
Description = "Scene Switcher for StarCraft II"
Creator = "Brain & Burny"
Version = "1.0.2"

#---------------------------------------
#	Set Variables
#---------------------------------------
debuggingMode = True
gameUrl = "http://localhost:6119/game"
uiUrl = "http://localhost:6119/ui"
configFile = "SC2SceneSwitcherConfig.json"
settings = {}
sceneSwitcher = {
    "checkThreadRunning": False,
}
currentScene = ""
lastSetScene = ""


#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
    global responseVariables, settings, configFile
    path = os.path.dirname(__file__)
    with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
        settings = json.load(file, encoding='utf-8-sig')
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
    global sceneSwitcher

    if settings["isEnabled"]:
        if not sceneSwitcher["checkThreadRunning"]:
            sceneSwitcher["checkThreadRunning"] = True
            threading.Thread(target=PerformSceneSwitch, args=()).start()
    return


def PerformSceneSwitch():
    global gameUrl, uiUrl, settings, currentScene, lastSetScene, sceneSwitcher
    try:
        uiResponse = json.loads(json.loads(
            Parent.GetRequest(uiUrl, {}))['response'])

        if settings["isCasterModeEnabled"]:
            if uiResponse["activeScreens"] == []:
                gameResponse = json.loads(json.loads(
                    Parent.GetRequest(gameUrl, {}))['response'])
                if gameResponse["isReplay"]:
                    currentScene = settings["obsSceneCasterInReplay"]
                else:
                    currentScene = settings["obsSceneCasterInGame"]
            else:
                currentScene = settings["obsSceneCasterInMenu"]
        else:
            if uiResponse["activeScreens"] == []:
                gameResponse = json.loads(json.loads(
                    Parent.GetRequest(gameUrl, {}))['response'])
                if gameResponse["isReplay"]:
                    currentScene = settings["obsSceneInReplay"]
                else:
                    currentScene = settings["obsSceneInGame"]
            else:
                currentScene = settings["obsSceneInMenu"]

        if currentScene != "" and currentScene != lastSetScene:
            lastSetScene = currentScene
            #Parent.SetOBSCurrentScene(currentScene, callback)
            Parent.SetOBSCurrentScene(currentScene)

        sceneSwitcher["checkThreadRunning"] = False
    except Exception as e:
        sceneSwitcher["checkThreadRunning"] = False
        # TODO: a way to figure out how to display error message in case the streamer didnt connect ankhbbot with the OBS Remote plugin
        print("Unknown error while attempting to change scene", e)


def callback(string):
    Debug("error message: {}".format(string))


def Debug(message):
    if debuggingMode:
        Parent.Log("SceneSwitcher", message)

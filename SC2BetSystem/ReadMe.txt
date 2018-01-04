#################
Info
#################
Description: Automatic Betting System for the Game StarCraft II
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.2.0

#################
Variables in the Response Messages
#################
For more Informations about the variables you can use in the response Messages
check out the Link/File in the same Directory: "Overview - Usable Variables (opens Browser)"

#################
Overlay / Theme informations
#################
OBS BrowserSource Path: ..Scripts\SC2BetSystem\Overlays\index.html

# SC2Board
BrowserSource Size for "SC2Board":      Width: 645px - Height: 316px 
You can set the FadeIn Animation in the "userSettings.js" file which is located in '..\SC2BetSystem\Overlays\'.
You got 4 options to choose from which are written there. IMPORTANT: Keep in mind that those are case-sensitive! (TopDown, BottomUp, LeftRight, RightLeft)

# SC2ScoreBoard
BrowserSource Size for "SC2ScoreBoard": Width: 719px - Height: 68px


################
Usage
################
Download the current Streamlabs Chatbot version: https://streamlabs.com/chatbot

Download and install Python 2.7.13 since that's needed for Chatbot and the Script features: 
https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi 

Open the SL Chatbot and go to the "Scripts" tab in the left sidebar.
Click on the cogwheel in the top right and set your Python directory to the `Lib` folder where you installed Python 
(By default it should be `C:\Python27\Lib`).

Copy the scripts you want to use into the folder from the SL Chatbot. You can also use the Import function per button on the top right in the "Scripts" tab.
(By default it should be `C:\Users\<Username>\AppData\Roaming\AnkhHeart\AnkhBotR2\Twitch\Scripts`)

Go back to the `Scripts` tab in Chatbot and rightclick the background and click "Reload Scripts". 
Afterwards the list of installed scripts should appear and you can start configuring those.

To enable overlays you need to click the `Insert API Key` on the contextmenu by rightclicking on the script in Chatbot.


###############
Version History
###############
1.2.0
  ~ Completely overhauled the sidebar menu for the script (Arrangements, labels, tooltips, etc)
  ~ Added a dropdown menu to choose from themes
  ~ Added a "SC2ScoreBoard" theme which is smaller and especially created for showing on the top border of the screen
  ~ Users can now create their own themes easily without touching existing ones
  ~ Users can also create specific variables for seperate themes (userSettings)
  ~ Added "Configure Options" for set up and test purposes
    ~ Button to do a "Test Bet": Start, Update and showing a winner
    ~ Option to be able to test it live against "AI opponents"
    ~ Option to be able to bet/vote multiple times to test alone
    ~ Option to always show the Betting overlay to adjust your OBS BrowserSource neatly
    
  ~ Fixed LOTS OF SHIT (Too lazy to write all down :D )
  ~ Reworked the core code

1.1.3
  ~ Fixed issue where both players had a name found in the list of "StarCraft II Accounts"
  ~ In case users enter wrong StarCraft Names (like with trailing white space or with character code, e.g. Burny#1337), it will now automatically correct them
  ~ Renamed "StarCraft II Accounts" to "Player Names"
  ~ Necessary changes since AnkhBot became Streamlabs Chatbot

1.1.2
  ~ Added dev options - testing overlay vs AI and multiple entries
  ~ Added Voting system (either without currency or with currency and a fixed amount)
  ~ Added ability to display percentages of amount of votes / amount of currency worth of bets  
  ~ Removed "Betting Enabled" because Ankhbot put in its own enabler

1.1.1:
  ~ Replaced "requests" with "urllib2"
  ~ Fixed some stuff

1.1.0:
  ~ Added Overlay System
	+ First Design: StarCraft II

1.0.0:
  ~ First Release version


###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.

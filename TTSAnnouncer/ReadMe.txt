#################
Info
#################

Description: Text-to-Speech Announcer
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.0.1

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


To get the script working:

After loading the script in StreamlabsBot, go to 
https://warp.world/scripts/tts-message

In the field "Browser Source:" (e.g. http://tts.warp.world:5500/tts/uJEtMSRyrS2qjLn/burnysc2 ) is your key (here: "uJEtMSRyrS2qjLn") - copy it to the field "Unique Key" in the TTS-Queue Script.
Caution: If your key is visible on stream, it may cause people to spam TTS (without using !tts <text> in chat). Simply generate a new "Unique Key" to fix this.
Open OBS and add a new browser source with the URL same as the one gathered from "Browser Source:"

Tip:
- If you don't want TTS Queue to be active in specific scenes, edit the TTS browser source scene in OBS and check "Shutdown source when not visible". Now, TTS won't be working in scenes where you don't have the TTS browser source active.


###############
Version History
###############

1.0.1:
  ~ First Release version


###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
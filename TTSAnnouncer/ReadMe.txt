#################
Info
#################
Description: Text-to-Speech Announcer
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.0.5


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


To get the script working just go to the menu "Get a link for your Browser Source" and click a button for a method you'd like to use.
The first button simply opens a tab in your default browser where you can use the URL there to use as your browser source link in the OBS source.
The second button let's your bot whisper your streamer account the link per Twitch. 
Important Notice: However this doesn't work if the streamer account is used also as bot account or if neither is connected!

Tip:
- If you don't want TTS Queue to be active in specific scenes, edit the TTS browser source scene in OBS and check "Shutdown source when not visible". Now, TTS won't be working in scenes where you don't have the TTS browser source active.


###############
Version History
###############
1.0.5:
  ~ Fixed a bug where the unique key file didn't load correctly

1.0.4:
  ~ Added two buttons to generate your OBS Browser Source link
  ~ Removed Unique Keys
  ~ Reorganised the sidebar (UI_config)

1.0.3:
  ~ Change "Point Cost" to numberfield instead of slider
  ~ Bugfix response when user has not enough points

1.0.2:
  ~ Fixed a bug where an error occurs without saving first. 
  ~ Fixed a bug which happens when you leave the blacklist empty.

1.0.1:
  ~ First Release version


###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.

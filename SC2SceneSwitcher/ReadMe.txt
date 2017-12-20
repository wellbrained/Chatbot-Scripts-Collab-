#################
Info
#################
Description: Automatic OBS Scene Switcher the Game StarCraft II
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.0.2


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

Don't forget to enable the checkbox "Enable OBS Scene Switcher" and then the scene switcher should work for you!

###############
Version History
###############
1.0.2:
  ~ Using multithreading now, because it seemed the script slowed down Ankhbot a lot - fixed!
  ~ Necessary changes since AnkhBot became Streamlabs Chatbot

1.0.1:
 ~ Compatibility with the new AnkhBot version

1.0.0:
  ~ First Release version

###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
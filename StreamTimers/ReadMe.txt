#################
Info
#################
Description: Uptime & Countdown with UI Interface
Created by: 
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
Version: 1.1.2


################
Usage
################
This script creates two text files called "Uptime.txt" and "Countdown.txt" in the following path: "..\AnkhBotR2\Twitch\Files".
For usage add them as textsource in your streaming software (OBS) or just by simply drag'n'drop into it.

# Uptime.txt: 
Displays the uptime of your running stream in the format you want.
It will automatically start counting up when your stream is indicated as live on Twitch and will reset itself after your stream was offline longer then the "Max Sleep Timer".
If your stream got interrupted by a crash on OBS or Twitch is having problems it stops counting up.
If you reconnect/restart your stream within the "Max Sleep Timer" the uptime will continue again. 

# Countdown.txt:
Displays a simple countdown in a format you want and after the countdown reaches 0 it will show the text from the "Custom Text after Countdown" textbox.


You can also set the countdown and uptime manually by using the commands in the respective area in the Scripts sidebar.
"Set countdown chat command" & "Set uptime chat command".

Use that specific command + the amount of time in minutes you want to set it to.
Example: !countdown 5 (Sets the countdown to 5 minutes)
Example: !setuptime 150 (Sets the uptime to 2 hours and 30 minutes)


###############
Version History
###############
1.1.2:
 ~ If the stream was running and then turned offline, the script will run until "Max Sleep Timer" has been reached and then reset the uptime, if the stream has not gone back online in the meantime.
 ~ If Streamlabs Chatbot is started while the stream is offline, it will also set the uptime back to zero.
 ~ The commands are now used with minutes (previously seconds). "!countdown 5" will set it to 5 minutes.
1.1.1:
 ~ Necessary changes since AnkhBot became Streamlabs Chatbot
1.1.0:
 ~ Added custom chat commands to set Countdown and Uptime
 ~ Added the option to display responses to the commands
1.0.3:
 ~ Bugfix for Uptime/Countdown
 ~ Default values are correct now
1.0.2:
 ~ Included the ScriptToggled-Function
 ~ Bugfix for Uptime
 ~ Set default values
1.0.1:
 ~ Reset now properly resets the Countdown in the textfile
 ~ UTF-8 Encoding integrated
1.0.0:
 ~ First Release version


###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.

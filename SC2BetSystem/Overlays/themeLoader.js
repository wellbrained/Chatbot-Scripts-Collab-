/*
###############
(c) Copyright
###############
Brain - www.twitch.tv/wellbrained
Burny - www.twitch.tv/burnysc2
All rights reserved. You may edit the files for personal use only.
*/

if (window.WebSocket) {
    //---------------------------------
    //  Variables
    //---------------------------------
	//  Connection Information
	var serviceUrl = "ws://127.0.0.1:3337/streamlabs"
	socket = null;

	if (typeof API_Key === "undefined") {
		$("body").html("ERROR: No API Key found!<br/>Rightclick on the SC2BetSystem script in Chatbot and select \"Insert API Key\"");
		$("body").css({"font-size": "20px", "color": "#ff8080", "text-align": "center"});
	}

	function Connect() {
		socket = new WebSocket(serviceUrl);

		socket.onopen = function() {
			var auth = {
				author: "Brain",
				website: "http://www.twitch.tv/wellbrained",
				api_key: API_Key,
				events: [
					"EVENT_INIT_THEME"
				]
			};
			socket.send(JSON.stringify(auth));
			console.log("Theme Loader Connected.");
		};

		socket.onmessage = function (message) {
			var jsonObject = JSON.parse(message.data);

			if (jsonObject.event == "EVENT_INIT_THEME") {
				SetThemeForOverlay(JSON.parse(jsonObject.data).themeName);
			} else {
				console.log("No theme selected.");
			}
		};

		socket.onerror = function(error) {
			console.log("Error: " + error);
		}

		socket.onclose = function() {
			console.log("Connection Closed!");
			HideBet();
			socket = null;
			setTimeout(function(){connectWebsocket()}, 5000);
		}
	}

	Connect();

	function SetThemeForOverlay(name) {
		console.log("SetThemeForOverlay: " + name);
		document.getElementById('themeBody').innerHTML = "<iframe src='" + name + "/index.html' width='100%' height='100%' frameborder='0' scrolling='no'></iframe>";
	}
};

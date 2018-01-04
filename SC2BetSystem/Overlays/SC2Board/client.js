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
	var reconnectIntervalMs = 10000;

	var hideOverlayAfterClosing = false;
	var showWinnerForSec = 3000;
	var setShowWinnerDuration = false;
	var betHidden = false;
	var fadeInType;
	var animationDuration = settings.animationDuration;

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
					"EVENT_BET_START",
					"EVENT_BET_END",
					"EVENT_BET_UPDATE",
					"EVENT_BET_ABORT",
					"EVENT_BET_WIN",
					"EVENT_BET_LOSE",
					"EVENT_INIT_THEME",
					"EVENT_BET_SHOW"
				]
			};
			socket.send(JSON.stringify(auth));
			console.log("Theme 'SC2Board' Connected");
		};

		socket.onmessage = function (message) {
			var jsonObject = JSON.parse(message.data);

			if (jsonObject.event == "EVENT_BET_START") {
				// Set FadeIn-Animation from userSettings.js
				console.log("FadeIn Animation: " + settings.fadeInAnimationType);
				fadeInType = settings.fadeInAnimationType;
				animationDuration = settings.animationDuration;
				StartBet(jsonObject.data);
			} else if (jsonObject.event == "EVENT_BET_END") {
				if (hideOverlayAfterClosing) {
					HideBet();
				}
			} else if (jsonObject.event == "EVENT_BET_UPDATE") {
				UpdateBet(jsonObject.data);
			} else if (jsonObject.event == "EVENT_BET_ABORT") {
				CloseBet();
			} else if (jsonObject.event == "EVENT_BET_WIN") {
				StreamerWins();
			} else if (jsonObject.event == "EVENT_BET_LOSE") {
				StreamerLoses();
			} else if (jsonObject.event == "EVENT_BET_SHOW") {
				console.log("DevEvent - Showing Bet");
				ShowBet();
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

	function StartBet(data) {
		var jsonObject = JSON.parse(data);
		console.log("Start new Bet");
		console.log(jsonObject);

		hideOverlayAfterClosing	= jsonObject.hideAfterBetClosed;
		if (!setShowWinnerDuration) {
			// Set duration timer for winner
			setShowWinnerDuration = true;
			showWinnerForSec = jsonObject.durationShowWinner;
			showWinnerForSec = showWinnerForSec+animationDuration;
		}

		$("h1").html(`${jsonObject.title}`);

		$("#p1Cmd").html(`${jsonObject.chatCmdWin}`);
		$("#player1").html(`<div id="p1Name">${jsonObject.player1}</div><span class='race ${jsonObject.race1}'></span>`);
		$("#p1Label").html(`${jsonObject.lblWin}`);
		if (jsonObject.isPercentageBased) {
			$("#p1BetBox").html(`${jsonObject.totalWin} %`);
		} else {
			$("#p1BetBox").html(`${jsonObject.totalWin} ${jsonObject.lblCurr}`);
		}

		$("#p2Cmd").html(`${jsonObject.chatCmdLose}`);
		$("#player2").html(`<span class='race ${jsonObject.race2}'></span><div id="p2Name">${jsonObject.player2}</div>`);
		$("#p2Label").html(`${jsonObject.lblLose}`);
		if (jsonObject.isPercentageBased) {
			$("#p2BetBox").html(`${jsonObject.totalLose} %`);
		} else {
			$("#p2BetBox").html(`${jsonObject.totalLose} ${jsonObject.lblCurr}`);
		}

		//added these in case the ankhbot script is reloaded before removing the class
		$("#p1BetBox").removeClass("betWinner");
		$("#p2BetBox").removeClass("betWinner");

		ShowBet();
	}

	function UpdateBet(data) {
		var jsonObject = JSON.parse(data);
		console.log("Bet was updated");
		console.log(jsonObject);

		if (jsonObject.isPercentageBased) {
			$("#p1BetBox").html(`${jsonObject.totalWin} %`);
			$("#p2BetBox").html(`${jsonObject.totalLose} %`);
		} else {
			$("#p1BetBox").html(`${jsonObject.totalWin} ${jsonObject.lblCurr}`);
			$("#p2BetBox").html(`${jsonObject.totalLose} ${jsonObject.lblCurr}`);
		}

		if (jsonObject.totalWin > jsonObject.totalLose) {
			$("#p2BetBox").removeClass("betWinner");
	        $("#p1BetBox").addClass("betWinner");
		} else if (jsonObject.totalWin < jsonObject.totalLose) {
			$("#p1BetBox").removeClass("betWinner");
	        $("#p2BetBox").addClass("betWinner");
		} else {
			$("#p1BetBox").removeClass("betWinner");
			$("#p2BetBox").removeClass("betWinner");
		}
	}

	function StreamerWins() {
		console.log("Streamer won");
		// When hidden add a second for the FadeIn Animation
		if (betHidden) {
			ShowBet();
			showWinnerForSec = showWinnerForSec+2000;
		}
        $("#player1").addClass("winner");
	    setTimeout(function(){
			CloseBet();
	    }, showWinnerForSec);
	}

	function StreamerLoses() {
		console.log("Streamer lost");
		// When hidden add a second for the FadeIn Animation
		if (betHidden) {
			ShowBet();
			showWinnerForSec = showWinnerForSec+2000;
		}
        $("#player2").addClass("winner");
	    setTimeout(function(){
			CloseBet();
	    }, showWinnerForSec);
	}

	function ShowBet() {
		console.log("Show Bet");
		var tl = new TimelineLite();

		if (fadeInType == "TopDown") {
			$("#container").css("top", "-350px");
		} else if (fadeInType == "BottomUp") {
			$("#container").css("top", "350px");
		} else if (fadeInType == "LeftRight") {
			$("#container").css("left", "-650px");
		} else if (fadeInType == "RightLeft") {
			$("#container").css("left", "650px");
		};

		tl.fromTo("#container", 2, { opacity: 0}, { opacity: 1});

		if (fadeInType == "TopDown") {
			tl.fromTo("#container", 2, { top: -350 }, { top: 0 });
		} else if (fadeInType == "BottomUp") {
			tl.fromTo("#container", 2, { top: 350 }, { top: 0 });
		} else if (fadeInType == "LeftRight") {
			tl.fromTo("#container", 2, { left: -650 }, { left: 0 });
		} else if (fadeInType == "RightLeft") {
			tl.fromTo("#container", 2, { left: 650 }, { left: 0 });
		};
	}

	function HideBet() {
		console.log("Hide Bet");
		var tl = new TimelineLite();

		if (fadeInType == "TopDown") {
			tl.fromTo("#container", 2, { top: 0 }, { top: -350 });
		} else if (fadeInType == "BottomUp") {
			tl.fromTo("#container", 2, { top: 0 }, { top: 350 });
		} else if (fadeInType == "LeftRight") {
			tl.fromTo("#container", 2, { left: 0 }, { left: -650 });
		} else if (fadeInType == "RightLeft") {
			tl.fromTo("#container", 2, { left: 0 }, { left: 650 });
		}
		tl.fromTo("#container", 2, { opacity: 1}, { opacity: 0});
		betHidden = true;
	}

	function CloseBet() {
		console.log("Close Bet completely");

		HideBet();

		$("#player1").removeClass("winner");
		$("#player2").removeClass("winner");
		$("#p1BetBox").removeClass("betWinner");
		$("#p2BetBox").removeClass("betWinner");
		setShowWinnerDuration = false;
	}
};

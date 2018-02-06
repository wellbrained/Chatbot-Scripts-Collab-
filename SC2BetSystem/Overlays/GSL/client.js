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
	var streamerWon;

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
			console.log("Theme 'GSL' Connected");
		};

		socket.onmessage = function (message) {
			var jsonObject = JSON.parse(message.data);

			if (jsonObject.event == "EVENT_BET_START") {
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

		if (jsonObject.capitalizeNames) {
			$(".name").css("text-transform", "uppercase");
		}

		$("#player1 .name").html(`<span class='race ${jsonObject.race1}'></span>${jsonObject.player1}`);
		$("#player2 .name").html(`<span class='race ${jsonObject.race2}'></span>${jsonObject.player2}`);

		$("#player1 .bets").text(`${jsonObject.chatCmdWin}`);
		$("#player2 .bets").text(`${jsonObject.chatCmdLose}`);

		// Decide percentage or total amount
		if (jsonObject.isPercentageBased) {
			$("#stat-left span").html(`${jsonObject.totalWin} %`);
			$("#stat-right span").html(`${jsonObject.totalLose} %`);
		} else {
			$("#stat-left span").html(`${jsonObject.totalWin} ${jsonObject.lblCurr}`);
			$("#stat-right span").html(`${jsonObject.totalLose} ${jsonObject.lblCurr}`);
		}

		ShowBet();
	}

	function UpdateBet(data) {
		var jsonObject = JSON.parse(data);
		console.log("Bet was updated");
		console.log(jsonObject);

		if (jsonObject.isPercentageBased) {
			$("#stat-left span").html(`${jsonObject.totalWin} %`);
			$("#stat-right span").html(`${jsonObject.totalLose} %`);
		} else {
			$("#stat-left span").html(`${jsonObject.totalWin} ${jsonObject.lblCurr}`);
			$("#stat-right span").html(`${jsonObject.totalLose} ${jsonObject.lblCurr}`);
		}
	}

	function StreamerWins() {
		console.log("Streamer won");
		streamerWon = true;

		ShowBet();

	    setTimeout(function(){
			CloseBet();
		}, showWinnerForSec+5000);
	}

	function StreamerLoses() {
		console.log("Streamer lost");
		streamerWon = false;
		ShowBet();

	    setTimeout(function(){
			CloseBet();
	    }, showWinnerForSec+5000);
	}

	function ShowBet() {
		console.log("Show Bet");
		var tl = new TimelineLite();
		tl.to("#container", 2, { top: 0 });

		console.log("StreamerWon: " + streamerWon);
		if (typeof streamerWon === 'boolean' && streamerWon) {
			$("#stat-left span").html("WINNER");
			$("#stat-right").css("opacity", 0);
		}
		if (typeof streamerWon === 'boolean' && !streamerWon) {
			$("#stat-right span").html("WINNER");
			$("#stat-left").css("opacity", 0);
		}
		tl.to("#stats", 2, { top: 5 });
	}

	function HideBet() {
		console.log("Hide Bet");
		var tl = new TimelineLite();
		tl.to("#stats", 2, { top: -40 });
		tl.to("#container", 2, { top: -125 });
		betHidden = true;
	}

	function CloseBet() {
		console.log("Close Bet completely");
		HideBet();
	}
};

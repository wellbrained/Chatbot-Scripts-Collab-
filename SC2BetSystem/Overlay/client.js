if (window.WebSocket) {
    //---------------------------------
    //  Variables
    //---------------------------------
	//  Connection Information
	var serviceUrl = "ws://127.0.0.1:3337/AnkhBot"
	socket = null;
	var reconnectIntervalMs = 10000;

	var showWinnerForSec = 3000;
	var bSetWinDuration = false;
	var bHideAfterBetClosed = false;
	var bHiddenBet = false;
	var fadeInType = "";


	// Connect if API_Key is inserted
	// Else show an error on the overlay
	if (typeof API_Key === "undefined") {
		$("body").html("ERROR: No API Key found!<br/>Rightclick on the Scoreboard script in AnkhBot and select \"Insert API Key\"");
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
					"EVENT_BET_LOSE"
				]
			};
			socket.send(JSON.stringify(auth));
			console.log("Connected");
		};

		socket.onmessage = function (message) {
			console.log("Check for Events function");
			var jsonObject = JSON.parse(message.data);
				
			if (jsonObject.event == "EVENT_BET_START") {
				console.log("Animation Type: " + JSON.parse(jsonObject.data).animationType);
				fadeInType = JSON.parse(jsonObject.data).animationType;
				StartBet(jsonObject.data);
			} else if (jsonObject.event == "EVENT_BET_END") {
				console.log("Close Bettting");
				if (bHideAfterBetClosed) {
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

		bHideAfterBetClosed = jsonObject.hideAfterBetClosed;

		if (!bSetWinDuration) {
			showWinnerForSec = jsonObject.durationShowWinner;
			bSetWinDuration = true;
		}

		$("h1").html(`${jsonObject.title}`);
		
		$("#p1Cmd").html(`${jsonObject.chatCmdWin}`);
		$("#player1").html(`<div id="p1Name">${jsonObject.player1}</div><span class='race ${jsonObject.race1}'></span>`);
		$("#p1Label").html(`${jsonObject.lblWin}`);
		$("#p1BetBox").html(`${jsonObject.totalWin} ${jsonObject.lblCurr}`);
		
		$("#p2Cmd").html(`${jsonObject.chatCmdLose}`);
		$("#player2").html(`<span class='race ${jsonObject.race2}'></span><div id="p2Name">${jsonObject.player2}</div>`);
		$("#p2Label").html(`${jsonObject.lblLose}`);
		$("#p2BetBox").html(`${jsonObject.totalLose} ${jsonObject.lblCurr}`);

		ShowBet();
	}

	function UpdateBet(data) {
		var jsonObject = JSON.parse(data);
		console.log("Registered new Bet");
		console.log(jsonObject);

		$("#p1BetBox").html(`${jsonObject.totalWin} ${jsonObject.lblCurr}`);
		$("#p2BetBox").html(`${jsonObject.totalLose} ${jsonObject.lblCurr}`);

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
		if (bHiddenBet) {
			ShowBet();
			showWinnerForSec = showWinnerForSec+1000;
		}
        $("#player1").addClass("winner");
	    setTimeout(function(){
			CloseBet();
	    }, showWinnerForSec);
	}

	function StreamerLoses() {
		console.log("Streamer lost");
		if (bHiddenBet) {
			ShowBet();
			showWinnerForSec = showWinnerForSec+1000;
		}
        $("#player2").addClass("winner");
	    setTimeout(function(){
			CloseBet();
	    }, showWinnerForSec);
	}

	function ShowBet() {
		console.log("Show Bet");
		if (fadeInType == "TopDown") {
			$("#container").css("top", "-350px");
		} else if (fadeInType == "BottomUp") {
			$("#container").css("top", "350px");
		} else if (fadeInType == "LeftRight") {
			$("#container").css("left", "-650px");
		} else if (fadeInType == "RightLeft") {
			$("#container").css("left", "650px");
		};

		$("#container").css("opacity", "1");

		var tl = new TimelineLite();
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
			$("#container").css("left", "-650px");
			tl.fromTo("#container", 2, { left: 0 }, { left: -650 });
		} else if (fadeInType == "RightLeft") {
			$("#container").css("left", "-650px");
			tl.fromTo("#container", 2, { left: 0 }, { left: 650 });
		}
		$("#container").css("opacity", "0");
		bHiddenBet = true;
	}

	function CloseBet() {
		console.log("Close Bet completely");

		HideBet();

		$("#player1").removeClass("winner");
		$("#player2").removeClass("winner");
		$("#p1BetBox").removeClass("betWinner");
		$("#p2BetBox").removeClass("betWinner");
		bSetWinDuration = false;
	}
};
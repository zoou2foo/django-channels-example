console.log("Sanity check from room.js");

const roomName = JSON.parse(document.getElementById('roomName').textContent);

let chatLog = document.querySelector("#chatLog");
let chatMessageInput = document.querySelector("#chatMessageInput");
let chatMessageSend = document.querySelector("#chatMessageSend");
let onlineUsersSelector = document.querySelector("#onlineUsersSelector");

// adds a new option to 'onlineUsersSelector'
function onlineUsersSelectorAdd(value) {
	if (document.querySelector("option[value='" + value + "']")) return;
	let newOption = document.createElement("option");
	newOption.value = value;
	newOption.innerHTML = value;
	onlineUsersSelector.appendChild(newOption);
}

// removes an option from 'onlineUsersSelector'
function onlineUsersSelectorRemove(value) {
	let oldOption = document.querySelector("option[value='" + value + "']");
	if (oldOption !== null) oldOption.remove();
}

// focus 'chatMessageInput' when user opens the page
chatMessageInput.focus();

// submit if the user presses the enter key
chatMessageInput.onkeyup = function(e) {
	if (e.keyCode === 13) { // enter key
		chatMessageSend.click();
	}
};

// clear the 'chatMessageInput' and forward the message
chatMessageSend.onclick = function() {
	if (chatMessageInput.value.length === 0) return;
	chatSocket.send(JSON.stringify({ // send the message to the WebSocket
		"message": chatMessageInput.value, // the message
	}));
	chatMessageInput.value = ""; // clear the 'chatMessageInput'
};

let chatSocket = null;

// connect to the WebSocket
function connect() {
	chatSocket = new WebSocket("ws://" + window.location.host + "/ws/chat/" + roomName + "/"); //would it be here to change it to wss?

	chatSocket.onopen = function(e) {
		console.log("Successfully connected to the WebSocket.")
	}

	// 'onclose' event handler
	chatSocket.onclose = function(e) {
		console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s");
		setTimeout(function() {
			console.log("Reconnecting...");
			connect(); // try to reconnect; so we call back the connect function
		}, 2000); // try to reconnect after 2s
	};

	// 'onmessage' event handler
	chatSocket.onmessage = function(e) {
		const data = JSON.parse(e.data);
		console.log(data);

		switch (data.type) { // determined the message type
			case "chat_message":
				chatLog.value += data.user + ": " + data.message + "\n";
				break;
			case "user_list":
				for (let i = 0; i < data.users.length; i++) {
					onlineUsersSelectorAdd(data.users[i]);
				}
				break;
			case "user_join":
				chatLog.value += data.user + " joined the chat.\n";
				onlineUsersSelectorAdd(data.user);
				break;
			case "user_leave":
				chatLog.value += data.user + " left the room.\n";
				onlineUsersSelectorRemove(data.user);
				break;
			default:
				console.error("Unknown message type!");
				break;
		}
		//scroll 'chatLog' to the bottom
		chatLog.scrollTop = chatLog.scrollHeight;
	};

	// 'onerror' event handler
	chatSocket.onerror = function(err) {
		console.log("WebSocket encountered an error: " + err.message);
		console.log("Closing the socket.");
		chatSocket.close();
	}
}
connect();
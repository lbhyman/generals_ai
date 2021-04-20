var path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../constants.env') });
var env = process.env;

//const fork = require('child_process').fork;
//process.env.FLASK_APP='online_bot.py'
//execSync('fuser -k 5000/tcp')
//fork('flask run')

const readline = require('readline').createInterface({
	input: process.stdin,
	output: process.stdout
});

var fetch = require('node-fetch');

// socket.io-client version: 1.7.2
var io = require('socket.io-client');
console.log(process.env.SOCKET_ADDRESS);
var socket = io(env.SOCKET_ADDRESS);

socket.on('disconnect', function() {
	console.error('Disconnected from server.');
	process.exit(1);
});

socket.on('connect', function() {
	console.log('Connected to server.');
	var user_id = env.USER_ID;
	var username = env.USERNAME;
	// Set the username for the bot
	if (!env.USERNAME_SET) {
		readline.question('Bot Username: ', name => {
			username = name;
			socket.emit('set_username', user_id, username);
			env.USERNAME = username;
			readline.close();
		})
		env.USERNAME_SET = true;
	}
	// Join a private lobby
	function join_game(id) {
		socket.emit('join_private', id, user_id);
		socket.emit('set_force_start', id, true);
		console.log('Joined custom game at http://bot.generals.io/games/' + encodeURIComponent(id));
	}
	readline.question('Custom Game ID: ', id => {
		if (id === '') {
			join_game(env.CUSTOM_GAME_ID);
		}
		else {
			join_game(id);
			env.CUSTOM_GAME_ID = id;
		}
		readline.close();

	})
});

socket.on('game_start', function(data) {
	// Get ready to start playing the game.
	fetch('http://127.0.0.1:5000/game_start', 
		{headers: {'Content-Type': 'application/json'},
		method: 'POST',
		body: JSON.stringify(data)
	}).then(function (response) {
		return response.text();
	})	
	var replay_url = 'http://bot.generals.io/replays/' + encodeURIComponent(data.replay_id);
	console.log('Game starting! The replay will be available after the game at ' + replay_url);
});

socket.on('game_update', function(data) {
	// Send the update to the bot and receive bot's move choice
	fetch('http://127.0.0.1:5000/handle_update', 
		{headers: {'Content-Type': 'application/json'},
		method: 'POST',
		body: JSON.stringify(data)
	}).then(function (response) {
		return response.json();
	}).then(function (json) {
		socket.emit('attack', json.start_index, json.end_index);
	})
});

function leaveGame() {
	socket.emit('leave_game');
}

socket.on('game_lost', leaveGame);

socket.on('game_won', leaveGame);
from flask import Flask, jsonify, request
from random_agent import RandomAgent

online_bot = Flask(__name__)
agent = RandomAgent()

@online_bot.route('/game_start', methods=['GET', 'POST'])
def game_start():
    # POST request
    if request.method == 'POST':
        index = int(request.get_json()['playerIndex'])
        agent.set_player_index(index)
        return 'OK', 200
    
    # GET request
    else:
        return 'OK', 200       
    
@online_bot.route('/handle_update', methods=['GET', 'POST'])
def handle_update():
    # POST request
    if request.method == 'POST':
        agent.update(request.get_json())
        start_index, end_index = agent.next_move()
        return jsonify({'start_index': start_index, 'end_index': end_index}), 200
    
    # GET request
    else:
        return jsonify(agent.next_move()), 200
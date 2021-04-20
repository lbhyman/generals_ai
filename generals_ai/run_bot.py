import socketio
from os import environ
from dotenv import load_dotenv
from random_agent import RandomAgent
from pathlib import Path
import sys
import time

def main():
    # Environment variables
    load_dotenv(Path('..') / 'constants.env')
    user_id = environ.get('USER_ID')
    username = environ.get('USERNAME')
    game_id = environ.get('CUSTOM_GAME_ID')

    # AI agent
    agent = RandomAgent()

    # Socketio client and callbacks
    client = socketio.Client(reconnection_attempts=10,logger=True, engineio_logger=True)

    @client.event
    def connect():
        #client.emit('set_username', data=(user_id, username))
        client.emit('join_private', data=(game_id, user_id))
        client.call('set_force_start',data=(game_id, 1,True))
        print("Connected to server")    
    
    @client.event
    def queue_update(data):
        client.emit('set_force_start', data=(game_id, True))
        
    @client.event
    def connect_error():
        client.emit('leave_game')
        print("Connection error")
        
    @client.event
    def disconnect():
        client.emit('leave_game')
        client.emit('leave_private', data=(game_id, user_id))
        print("Disconnected from server")
        sys.exit(1)
        
    @client.event
    def game_start(data):
        agent.set_player_index(data.playerIndex)
        print("Game started")
        
    @client.event
    def game_update(data):
        agent.update(data)
        start_position, end_position = agent.next_move()
        client.emit('attack', data=(start_position, end_position))
        
    @client.event
    def game_won():
        client.emit('leave_game')
        
    @client.event
    def game_lost():
        client.emit('leave_game')

    client.connect(environ.get('SOCKET_ADDRESS'), socketio_path='socket.io', transports='websocket')
    #client.wait()
    
if __name__=='__main__':
    main()
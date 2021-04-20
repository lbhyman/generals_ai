
import socketio
client = socketio.Client()
client.connect('http://bot.generals.io', socketio_path='socket.io', transports='websocket')

'''
from websocket import create_connection, WebSocketConnectionClosedException
_ENDPOINT = "ws://botws.generals.io/socket.io/?EIO=3&transport=websocket"
ws = create_connection(_ENDPOINT)'''
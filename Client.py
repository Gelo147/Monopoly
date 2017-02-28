from socket import *
import json
from threading import Thread
from hashlib import sha256
from queue import Queue
from Board import Board


class Client:
    BROADCAST_PORT = 44470
    TRANSMIT_PORT = 44469
    BROADCAST_ADDRESS = "255.255.255.255"
    BOARD_FILE = "text/DublinBoard.txt"

    def __init__(self):
        # setup the client
        self._connection_queue = Queue()

        self._broadcaster = Thread(target=self._broadcast, args=(self.BROADCAST_PORT))
        self._broadcaster.start()
        self._transmitter = Thread(target=self._transmit, args=(self.TRANSMIT_PORT))
        self._transmitter.start()
        self._open_games = []

        self._board = None
        self._local_player = None


    def createGame(self, username, password):
        # inform the server we wish to create a game
        try:
            sock_create = socket()
            #password = sha256(password.encode()).hexdigest()
            data = json.dumps(({"command": "CREATE", "values": {"game": "Monopoly",
                                                                "username": username,
                                                                "password": password}}))
            sock_create.sendall(data.encode())
            data = None
            while not data:
                data, address = sock_create.recvfrom(1024)
                sock_create.connect((address[0], self.TRANSMIT_PORT))
                data = json.loads(data.decode())
        except timeout:
            pass
        if data == "1":
            sock_create.close()

    def test():
    	address = self.poll()
    	self.join(address, "conortwo", "psswd")

    def poll(self):
    	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        data = json.dumps({"command": "POLL"})
        s.sendto(data.encode(), ("255.255.255.255", 44470))
        data = None
        while data == None:
            data, addr = s.recvfrom(1024)
            data = json.loads(data.decode())
            print(data)
            assert data["command"] == "GAME"
            assert data["values"]["game"]["name"] == "Monopoly"
            print(data["command"])
        s.close()
        return addr[0]

    def join(self, address, username, password):
    	# ask to join a specific game with username and password
    	sock_join = socket()
    	sock_join.connect(address,Client.TRANSMIT_PORT)
    	data = json.dumps(({"command": "JOIN", "values": {"username": username,"password":password}}))
    	data = sock_join.sendall(data.encode())
    	print("DATA: ",data)
    	data = None
    	while not data:
    		data = sock_join.recv(1024).decode()
    		if data:
    			print("DATA: ",data)



    def listGames(self):
    	# returns a list of games client has heard about
    	return self._open_games

    def _transmit(self, transmit_port):
        # to be run in a thread and handle outgoing messages to specific server
        pass

    def _broadcast(self):
        # to be run in a thread and handle broadcast messages to find server(s)
        pass

    def _newGame(self,data):
    	# handles a GAME message from the server by adding it to the list of open games
    	playernames = data["game"]["players"]
    	password_protected = data["game"]["password"]
    	self._open_games.append([playernames,password_protected])

    def _gameStart(self,data):
    	# handles a START message from server by creating the board and passing it to GUI
    	players = data["players"]
    	local_id = data["local"]
    	self._board = Board(self.BOARD_FILE, players)
    	self._local_player = self._board.getPlayer(local_id)
    	#Gui.start(board,local_player)

    def _newTurn(self,data):
    	# handles a TURN message from the server by telling GUI who's turn has begun
    	player_id = data["player"]
    	#Gui.newTurn(player_id)

    def _hasQuit(self,data):
    	quitter = (data["player"])
    	self._board.removePlayer(quitter)

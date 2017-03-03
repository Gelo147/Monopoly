from socket import *
import json
from threading import Thread
from hashlib import sha256
from queue import Queue
from Board import Board
import time
from select import select


class Client:
    BROADCAST_PORT = 44470
    TRANSMIT_PORT = 44469
    BROADCAST_ADDRESS = "255.255.255.255"
    BOARD_FILE = "text/DublinBoard.txt"

    def __init__(self):
        # setup the client
        self._connection_queue = Queue()
        self._socket = None
        self._transmitter = Thread(target=self.addToQueue, args=())
        self._open_games = []

        self._board = None
        self._local_player = None

    """
    <-------------------- Game discovery and creation ------------------->
        Following methods are for setup before game has actually started
    <-------------------------------------------------------------------->
    """

    def createGame(self,address, username, password):
        # inform the server we wish to create a game
        try:
            sock_create = socket()
            sock_create.connect((address, Client.TRANSMIT_PORT))
            # password = sha256(password.encode()).hexdigest()
            data = json.dumps(({"command": "CREATE", "values": {"game": "Monopoly",
                                                                "username": username,
                                                                "password": password}}))
            sock_create.sendall(data.encode())
            data = None
            while not data:
                data = sock_create.recv(1024)
                data = json.loads(data.decode())
                if data:
                    print("response",data)
                if data and data["command"] == "CREATE" and data["values"] == '1':
                    print("game created successfully")
                    self._socket = sock_create
                    #self._transmitter.start()
        except timeout:
            pass

    def test(self):
        address = self.poll()
        print("server address",address)
        self.createGame(address,"conortwo", "psswd")
        time.sleep(1)
        self.start()
        while True:
            pass
        
    def poll(self):
        # used to discover any open games on the network
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        data = json.dumps({"command": "POLL"})
        s.sendto(data.encode(), ("255.255.255.255", 44470))
        data = None
        while data == None:
            data, addr = s.recvfrom(1024)
            data = json.loads(data.decode())
            print("Games found:",data)
        s.close()
        return addr[0]

    def join(self, address, username, password):
        # ask to join a specific game with username and password
        sock_join = socket()
        sock_join.connect((address, Client.TRANSMIT_PORT))
        data = json.dumps(({"command": "JOIN", "values": {"username": username, "password": password}}))
        data = sock_join.sendall(data.encode())
        print("DATA: ", data)
        data = None
        while not data:
            data = json.loads(sock_join.recv(1024).decode())
            if data and data["command"] == "JOIN" and data["values"] == '1':
                self._socket = sock_join
                #self._transmitter.start()

    def listGames(self):
        # returns a list of games client has heard about
        return self._open_games

    def addToQueue(self):
        while True:
            data = None
            while not data and self._socket:
                data = self._socket.recv(1024).decode()
            self._connection_queue.put(data)
    

    """
    <-------------------- Commands from GUI ----------------------------->
        Following methods are for communicating user intent to server
    <-------------------------------------------------------------------->
    """
    def start(self):
        # tell the server to start the game already
        data = json.dumps({"command":"START"})
        print("sent data",data)
        data = self._socket.sendall(data.encode())
        print("client socket",self._socket)
        data = None
        while not data:
            try:
                connections, write, exception = select([self._socket], [], [], 0.05)
                print(connections)
                for con in connections:
                    print("check data")
                    data = json.loads(con.recv(1024).decode())
                    print("server says",data)
                    if data and data["command"] == "START" and data["values"] == '1':
                        print("game has started")
            except Exception as e:
                print(e)
    
    def quit(self):
        # Tell the server that you wish to quit this game
        pass
    
    """
    <---------- Updating local state based on Server messages ----------->
        Following methods are for responding to Server messages and updating GUI
    <-------------------------------------------------------------------->
    """
    
    def _newGame(self, data):
        # handles a GAME message from the server by adding it to the list of open games
        playernames = data["game"]["players"]
        password_protected = data["game"]["password"]
        self._open_games.append([playernames, password_protected])

    def _gameStart(self, data):
        # handles a START message from server by creating the board and passing it to GUI
        players = data["players"]
        local_id = data["local"]
        self._board = Board(self.BOARD_FILE, players)
        self._local_player = self._board.getPlayer(local_id)

    # Gui.start(board,local_player)

    def _newTurn(self, data):
        # handles a TURN message from the server by telling GUI who's turn has begun
        player_id = data["player"]

    # Gui.newTurn(player_id)
    def _hasQuit(self, data):
        quitter = (data["player"])
        self._board.removePlayer(quitter)

    def _bought(self, data):
        # update the owner of some space in board to be player with given id
        player = Board.getPlayer(data["player_id"])
        space = Board.getSpace(data["tile"])
        player.addProperty(space)

    def _paid(self, data):
        # update one or two players balances as they have changed
        player_from = (data["player_from"])
        player_to = (data["player_to"])
        amount = (data["amount"])
        if player_from is not None:
            player = Board.getPlayer(player_from)
            player.takeMoney(amount)
        if player_to is not None:
            player = Board.getPlayer(player_to)
            player.addMoney(amount)

    def _jailed(self,data):
        # some player got sent to jail so change their jail status
        new_inmate = Board.getPlayer(data["player"])
        new_inmate.updateJailed(True)
        
    def _sentchat(self, data):
        # send a message from the server to the textbox display
        sent_by = data["player"]
        message = data["message"]
        if sent_by is not None:
            message = sent_by + ": " + message
        print(message)  # change to send chat for GUI?

    def _drewCard(self, data):
        # you drew a card so tell the GUI about it and check if you're on bail
        card_text = data["text"]
        bail_status = data["is_bail"]
        if bail_status:
            self._local.updateBail(bail_status)
        self._sentchat({"player": None, "message": "You drew the following card: " + card_text})


if __name__ == '__main__':
    c = Client()
    c.test()

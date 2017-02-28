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

        self._socket = None
        self._transmitter = Thread(target=self.addToQueue, args=())
        self._open_games = []

        self._board = None
        self._local_player = None

    def createGame(self, username, password):
        # inform the server we wish to create a game
        try:
            sock_create = socket()
            # password = sha256(password.encode()).hexdigest()
            data = json.dumps(({"command": "CREATE", "values": {"game": "Monopoly",
                                                                "username": username,
                                                                "password": password}}))
            sock_create.sendall(data.encode())
            data = None
            while not data:
                data, address = sock_create.recvfrom(1024)
                sock_create.connect((address[0], self.TRANSMIT_PORT))
                data = json.loads(data.decode())
            self._socket = sock_create
            self._transmitter.start()
        except timeout:
            pass
        if data == "1":
            sock_create.close()

    def test(self):
        address = self.poll()
        self.join(address, "conortwo", "psswd")

    def poll(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
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
        sock_join.connect((address, Client.TRANSMIT_PORT))
        data = json.dumps(({"command": "JOIN", "values": {"username": username, "password": password}}))
        data = sock_join.sendall(data.encode())
        print("DATA: ", data)
        data = None
        while not data:
            data = sock_join.recv(1024).decode()
            if data and data["command"] == "JOIN" and data["values"] == 1:
                self._socket = sock_join
                self._transmitter.start()

    def listGames(self):
        # returns a list of games client has heard about
        return self._open_games

    def _transmit(self, transmit_port):
        # to be run in a thread and handle outgoing messages to specific server
        pass

    def addToQueue(self):
        while True:
            data = None
            while not data and self._socket:
                data = self._socket.recv(1024).decode()
            self._connection_queue.put(data)

    """Methods which handle server messages below"""

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

    def _jailed(self, data):
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

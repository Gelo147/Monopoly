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
        self.transmitter = Thread(target=self._transmit, args=(self.TRANSMIT_PORT))
        self.transmitter.start()
        self._board = Board(self.BOARD_FILE, {0: "player 0", 1: "player 1", 2: "player 2", 3: "player 3"})
        self._local = Board.getPlayer(0)

    def create(self, username, password):
        # inform the server we wish to create a game
        try:
            sock_create = socket()
            password = sha256(password.encode()).hexdigest()
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
        finally:
            sock_create.close()

    def _transmit(self, transmit_port):
        # to be run in a thread and handle outgoing messages to specific server
        pass

    def _broadcast(self):
        # to be run in a thread and handle broadcast messages to find server(s)
        pass

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

    def _sentchat(self,data):
        # send a message from the server to the textbox display
        sent_by = data["player"]
        message = data["message"]
        if sent_by not None:
            message = sent_by + ": " + message
        print(message) #change to send chat for GUI?

    def _drewCard(self,data):
        # you drew a card so tell the GUI about it and check if you're on bail
        card_text = data["text"]
        bail_status = data["is_bail"]
        if bail_status:
            self._local.updateBail(bail_status)
        self._sentchat({"player":None,"message":"You drew the following card: " + card_text})




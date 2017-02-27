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
        # to be run in a thread and handle outgoing messages to server
        pass

    def _broadcast(self):
        # to be run in a thread and handle broadcast messages to find server(s)
        pass

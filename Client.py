from socket import *
import json
from threading import Thread
from hashlib import sha256
from Board import Board
import time
from select import select
import traceback
from queue import Queue

class Client:
    BROADCAST_PORT = 44470
    TRANSMIT_PORT = 44469
    BROADCAST_ADDRESS = "255.255.255.255"
    BOARD_FILE = "text/full_board.txt"

    def __init__(self):
        # setup the client
        self._gameover = False
        self._socket = None
        # self._transmitter = Thread(target=self.addToQueue, args=())
        self._listener = Thread(target=self._message_listener, args=())
        self._open_games = []
        self.gui = None
        self._board = None
        self._local_player = None
        self.message_q = Queue()

    """
    <-------------------- Game discovery and creation ------------------->
        Following methods are for setup before game has actually started
    <-------------------------------------------------------------------->
    """

    def createGame(self, address, username, password):
        # inform the server we wish to create a game
        if not address:
            address = self.poll()
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
                    print("response", data)
                if data and data["command"] == "CREATE" and data["values"]["status"] == '1':
                    print("game created successfully")
                    self._socket = sock_create
                    self._listener.start()
                    # self._transmitter.start()
        except timeout:
            pass

    def test(self):
        address = self.poll()
        create = input("Create game? y / n")
        if create == 'y':
            self.createGame(address, "conortwo", "psswd")
            input("want to start?")
            self.start()
        else:
            self.join(address, "player 2", "psswd2")

    def poll(self):
        # used to discover any open games on the network
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        data = json.dumps({"command": "POLL"})
        s.sendto(data.encode(), ("255.255.255.255", 44470))
        data = None
        while data == None:
            data, addr = s.recvfrom(1024)
            print("got",data)
            data = json.loads(data.decode())
            pw = ""
            playerlist = data["values"]["game"]["players"]
            password_protected = data["values"]["game"]["password"]
            if password_protected:
                pw = "[PASSWORD]"
            if playerlist:
                game_desc = playerlist[0] + "'s game. [" + str(len(playerlist)) + " players]" + pw
                self._open_games = [(game_desc, addr[0])]
            else:
                game_desc = "No players"
                self._open_games = [(game_desc, addr[0])]
        s.close()
        return addr[0]

    def join(self, address, username, password):
        # ask to join a specific game with username and password
        sock_join = socket()
        sock_join.connect((address, Client.TRANSMIT_PORT))
        data = json.dumps(({"command": "JOIN", "values": {"username": username, "password": password}}))
        data = sock_join.sendall(data.encode())
        data = None
        while not data:
            data = json.loads(sock_join.recv(1024).decode())
            if data and data["command"] == "JOIN" and data["values"]["status"] == '1':
                self._socket = sock_join
                self._listener.start()
                # self._transmitter.start()

    def listGames(self):
        # returns a list of games client has heard about
        self.poll()
        return self._open_games

    """def addToQueue(self):
        while True:
            data = None
            while not data and self._socket:
                data = self._socket.recv(1024).decode()
            self._connection_queue.put(data)"""

    def _message_listener(self):
        while not self._gameover:
            try:
                connections, write, exception = select([self._socket], [], [], 0.05)
                for con in connections:
                    try:
                        data = con.recv(4096).decode()
                        message = json.loads(data)
                        self._handle_message(message)
                    except ValueError:
                        if data:
                            if len(data.split('}{')) == 1:
                                print("Invalid JSON string received: " + data)
                            else:
                                print("Combined JSON payloads received: " + data)
                                messages = data.split('}{')
                                messages[0] += '}'
                                messages[-1] = '{' + messages[-1]
                                for i, payload in enumerate(messages[1: -1], 1):
                                    messages[i] = '{' + payload + '}'
                                for message in messages:
                                    try:
                                        message = json.loads(message)
                                        self._handle_message(message)
                                    except ValueError:
                                        print("Invalid JSON string received: " + message)
                                    except Exception as e:
                                        traceback.format_exc()

                    except Exception as e:
                        print("TCP Error 1 ", traceback.format_exc(), e)
            except KeyboardInterrupt:
                return
            except Exception as e:
                print(e)

    def _handle_message(self, data):
        # handles different messages from the server
        command = data["command"]
        print("Command:", command)
        if command == "START":
            self._gameStart(data)
        elif command == "GAMEOVER":
            self._gameOver(data)
        elif command == "ROLL":
            self._rolled(data)
        elif command == "CHAT":
            self._sentchat(data)
        elif command == "TURN":
            self._newTurn(data)
        elif command == "BUY?":
            self.buy(True)
        elif command == "BOUGHT":
            print("BOUGHT BUG", data)
            self._bought(data)
        elif command == "GOTO":
            self._movedTo(data)
        elif command == "JAIL":
            self._jailed(data)
        elif command == "PAY":
            self._paid(data)
        elif command == "CARD":
            self._drewCard(data)
        elif command == "QUIT":
            self._hasQuit(data)
        else:
            print("Something weird", data)

    def _waitResponse(self, command):
        while not self._timeout:
            message = self.connection_queue.get()
            if message:
                if message[0]["command"] == command:
                    return message
        return "timeout"

    """
    <-------------------- Commands from GUI ----------------------------->
        Following methods are for communicating user intent to server
    <-------------------------------------------------------------------->
    """

    def start(self):
        # tell the server to start the game already
        data = json.dumps({"command": "START"})
        print("sent data", data)
        data = self._socket.sendall(data.encode())
        """while not data:
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
                print(e)"""

    def roll(self):
        # tell the server that we wish to roll the dice and start our turn
        data = json.dumps({"command": "ROLL"})
        data = self._socket.sendall(data.encode())

    def buy(self, answer):
        # tell the server whether we wish to buy a property we landed on or not
        if answer:
            data = json.dumps({"command": "BUY", "values": {"buy": 1}})
        else:
            data = json.dumps({"command": "BUY", "values": {"buy": 0}})
        data = self._socket.sendall(data.encode())

    def chat(self, message):
        # send a chat message to the server to be broadcast to all other players
        data = json.dumps({"command": "CHAT", "values": {"text": message}})
        data = self._socket.sendall(data.encode())

    def quit(self):
        # Tell the server that you wish to quit this game
        data = json.dumps({"command": "QUIT"})
        data = self._socket.sendall(data.encode())
        self._gameover = True

    """
    <---------- Updating local state based on Server messages ----------->
        Following methods are for responding to Server messages and updating GUI
    <-------------------------------------------------------------------->
    """

    def _newGame(self, data):
        # handles a GAME message from the server by adding it to the list of open games
        playernames = data["values"]["game"]["players"]
        password_protected = data["values"]["game"]["password"]
        self._open_games.append([playernames, password_protected])

    def _gameStart(self, data):
        # handles a START message from server by creating the board and passing it to GUI
        print("starting game", data)
        players = data["values"]["players"]
        local_id = data["values"]["local"]
        self._board = Board(self.BOARD_FILE, players)
        self._local_player = self._board.getPlayer(local_id)
        print("you are",self._local_player,"lockal id", local_id)

    def _gameOver(self, data):
        self._sentchat({"values": {"player": None, "text": "Game over!"}})
        self._gameover = True


    def _newTurn(self, data):
        # handles a TURN message from the server by telling GUI who's turn has begun
        print("x")
        player_id = data["values"]["player"]
        local_id = self._local_player.getId()
        print(player_id, local_id)
        if player_id == local_id:
            print("y")
            self._sentchat({"values": {"player": None, "text": "It's your turn!"}})
            # input("start roll?")
            self.roll()
            self.chat("Chat message... pls send")
        else:
            print("z")
            self._sentchat(
                {"values": {"player": None, "text": "It's " + str(self._board.getPlayer(player_id)) + "'s turn!"}})

    # Gui.newTurn(player_id)
    def _hasQuit(self, data):
        quitter = (data["values"]["player"])
        self._sentchat(
            {"values": {"player": None, "text": str(self._board.getPlayer(quitter)) + " has left the game!"}})
        self._board.removePlayer(quitter)

    def _movedTo(self, data):
        # handles GOTO message by updating a players position to tile specified
        player = self._board.getPlayer(data["values"]["player"])
        space_position = data["values"]["tile"]
        space = self._board.getSpace(space_position)
        player.setPosition(space_position)

        self._sentchat({"values": {"player": None, "text": str(player) + " just moved to " + space.getText()}})

    def _bought(self, data):
        # update the owner of some space in board to be player with given id
        player = self._board.getPlayer(data["values"]["player"])
        space = self._board.getSpace(data["values"]["tile"])
        self._sentchat({"values": {"player": None,
                                   "text": str(player) + " just bought '" + space.getText() + "' for " + str(
                                       space.getPrice())}})
        player.addProperty(space)

    def _paid(self, data):
        # update one or two players balances as they have changed
        player_from = (data["values"]["player_from"])
        player_to = (data["values"]["player_to"])
        amount = (data["values"]["amount"])
        if player_from is not None:
            player = self._board.getPlayer(player_from)
            self._sentchat({"values": {"player": None, "text": str(player) + " just paid " + str(amount)}})
            player.takeMoney(amount)
        if player_to is not None:
            player = self._board.getPlayer(player_to)
            self._sentchat({"values": {"player": None, "text": str(player) + " just got paid " + str(amount)}})
            player.addMoney(amount)

    def _jailed(self, data):
        # some player got sent to jail so change their jail status
        new_inmate = self._board.getPlayer(data["values"]["player"])
        new_inmate.updateJailed()

    def _sentchat(self, data):
        # send a message from the server to the textbox display
        sent_by = data["values"]["player"]
        message = data["values"]["text"]
        if sent_by is None:
            sent_by = ">"
        else:
            sent_by += ": "
        message = sent_by + message
        self.message_q.put(message)  # change to send chat for GUI?

    def _drewCard(self, data):
        # you drew a card so tell the GUI about it and check if you're on bail
        print("Card ", data)
        card_text = data["values"]["text"]
        bail_status = data["values"]["is_bail"]
        print("card_text:", card_text, "bail_status:", bail_status)
        if bail_status:
            self._local_player.updateBail(bail_status)
        self._sentchat({"values": {"player": None, "text": "You drew the following card: " + card_text}})

    def _rolled(self, data):
        die1, die2 = data["values"]["roll"][0], data["values"]["roll"][1]
        self._sentchat({"values": {"player": None, "text": "You rolled a " + str(die1) + " and a " + str(die2)}})


if __name__ == '__main__':
    c = Client()
    c.test()

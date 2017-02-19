from socket import *
from json import dumps, loads
from threading import Thread
from random import randint
from select import select
from Board import Board
from Player import Player


class Server:
    BROADCAST_PORT = 44470
    SERVICE_PORT = 44469

    def __init__(self, broadcast_port=None, service_port=None):

        # <---------- NOTE ---------->
        # Does the Board object store Payer objects?
        # <---------- NOTE ---------->
        self.game = {
            "name": "Monopoly",
            "players": {},  # id: Player map
            "comms": {},  # socket: id map
            "comms_rev": {},  # id: socket map
            "board": Board(),
            "top_id": 0,
            "started": True,
        }

        self.discover = Thread(target=self._open_broadcast,
                               args=(broadcast_port if broadcast_port is not None else Server.BROADCAST_PORT,))
        self.discover.start()

        self.server = Thread(target=self._open_service,
                             args=((service_port if service_port is not None else Server.SERVICE_PORT),))
        self.server.start()

    def _open_service(self, port):
        self.service_sock = socket()
        self.service_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # self.service_sock.setblocking(0)
        self.service_sock.bind(('', port))
        self.service_sock.listen(10);
        print("Service Listening")
        while True:
            try:
                connections, write, exception = select([self.service_sock],[],[],0.05)
                for con in connections:
                    client_sock, address = con.accept()
                    data = loads(client_sock.recv(4096).decode())
                    try:
                        if data["command"] == "CREATE":
                            action = self.create_game
                        elif data["command"] == "JOIN":
                            action = self.join_game
                        elif data["command"] == "CHAT":
                            action = self.chat
                        elif data["command"] == "ROLL":
                            action = self.roll
                        elif data["command"] == "BUY":
                            action = self.buy
                        elif data["command"] == "SELL":
                            action = self.sell
                        elif data["command"] == "TURN":
                            action = self.turn
                        elif data["command"] == "ROLL":
                            action = self.roll
                        elif data["command"] == "GOTO":
                            action =self.go_to
                        elif data["command"] == "PAY":
                            action = self.pay
                        elif data["command"] == "CARD":
                            action = self.card
                        else:
                            #error message
                            pass
                        action(data,client_sock)
                    except Exception as e:
                        print("TCP Error 1 ",e)
                        client_sock.close()
            except timeout:
                pass
            except Exception as e:
                print("TCP Error 2 ",e)

    def _open_broadcast(self, broadcast_port):
        broadcastsock = socket(AF_INET, SOCK_DGRAM)
        broadcastsock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        broadcastsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        broadcastsock.bind(('', broadcast_port))
        broadcastsock.settimeout(1)
        print("Broadcast Ready")
        while True:
            try:
                data, address = broadcastsock.recvfrom(1024)
                data = loads(data.decode())
                if data["command"] == "POLL":
                    action = self.poll_games
                else:
                    action = self.unknown_command_error
                action(data, broadcastsock, address)
            except timeout:
                pass
            except Exception as e:
                print("Broadcast Error ",e)

    def unknown_command_error(self, data, broadcastsock, address):
        # {command:error}
        data = {"command": "ERROR",
                "values": "Unknown command"}
        self._send_answer(data, broadcastsock, address)

    """
    <-------------------- CLIENT TO SERVER ------------------------------>
        Following function get called buy requests from client or as
        "missing a word" to an action performed as a result of a broadcast
    <-------------------------------------------------------------------->
    """
    def create_game(self, data, sock):
        # called by request handler <function=_handle_broadcast> when
        # incoming message has <var=command> = CREATE
        # Returns: Success / Failure message
        self.game["comms"][self.game["top_id"]] = sock
        self.game["comms_rev"][sock] = self.game["top_id"]
        #add player to the player list
        self.game["players"][self.game["top_id"]] = Player(data["values"]["username"])
        self.game["top_id"] += 1
        print("=" * 50)
        print(self.game)
        print("="*50)
        data = {
            "command": "CREATE",
            "values": "1",
        }
        self._send_answer_tcp(sock,data)

    def poll_games(self, data, sock, address):
        # called by request handler <function=_handle_broadcast> when
        # incoming message has <var=command> = POLL
        # Returns: Game (ie. {"command": "GAME", "values": {"game":game_details}}
        data = {
            "command": "GAME",
            "values": {
                "game": {
                    "name": self.game["name"],
                    "players": [player.name for id, player in self.game["players"].items()]
                }
            }
        }
        self._send_answer(data, sock, address)

    def join_game(self, data, sock):
        # called by request handler <function=_handle_broadcast> when
        # incoming message has <var=command> = JOIN
        # Returns: Success / Failure message
        success = 0
        if not self.game["started"] and (self.game["top_id"] < 6):
            self.game["comms"][self.game["top_id"]] = sock
            self.game["comms_rev"][sock] = self.game["top_id"]
            # add player to the player list
            self.game["players"][self.game["top_id"]] = Player(data["values"]["username"])
            self.game["top_id"] += 1
            success = 1
        data = {
            "command": "JOIN",
            "values": success,
        }
        self._send_answer_tcp(sock, data)
        self._push_notification(data,sock)

    def _send_answer(self, data, sock, address):
        sock.sendto(dumps(data).encode(), address)

    def _send_answer_tcp(self,sock, data):
        sock.send(dumps(data).encode())

    def _push_notification(self,data,exclude=None):
        for sock in self.game["comms"]:
            if sock != exclude:
                sock.send(dumps(data).encode())

    """
    <-------------------- CLIENT TO SERVER ------------------------------>
        Following function get called buy requests from client or as
        "missing a word" to an action performed as a result of a request
    <-------------------------------------------------------------------->
    """

    def roll(self, values):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = ROLL
        # generates two random numbers in range(1,7)
        # Returns: ROLL message
        data = {
            "command": "ROLL",
            "values":{
                "roll": [randint(1,7), randint(1,7)],
]
            }
        }


    def buy(self, values):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = BUY
        # 'buys' the property that the player is currently on
        # Returns: Success / Failure message
        pass

    def sell(self, values):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = SELL
        # 'sells' the properties defined in <var=ids> inside <var=values>
        # Returns: PAY message
        pass

    def chat(self, values,sock):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = CHAT
        # Sends the message <var=text> that is in <var=values> onto other users,
        # attaching values like username onto the message

        # Returns: does not return just passes on ?? <-- NOTE * Not sure yet. * NOTE -->
        data = {
            "command": "CHAT",
            "values": {
                "text": values["text"],
                "from": self.game["comms"][sock].name
            }
        }

    def turn(self, values):
        # send message TURN to all clients
        # informing them of whose turn it is
        # <-- NOTE * self invoked sometimes?? * NOTE -->
        pass

    def go_to(self, values):
        # inform all players where one player is
        # {values: {palyer: int player_id, tile: int tile } }
        pass

    def pay(self, values):
        # transaction between player and player or bank and player if
        # to or from are None
        # {"command": "PAY",
        #    "values": {
        #        "from": int player_id or None,
        #        "to": int player_id or None,
        #        "amount": int amount
        #     }
        # }
        pass

    def card(self, values):
        # Comunity Chest / Chance cards
        #
        # {
        #    "command": "CARD",
        #    "values": {
        #        "text": str text,
        #        "is_bail": bool is_bail
        #    }
        # }
        pass

if __name__ == '__main__':
    Server()
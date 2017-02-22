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
            "players": [],  # player names
            "comms": {},  # socket: id map
            "comms_rev": {},  # id: socket map
            "board": Board(),
            "top_id": 0,
            "started": True,
            "turn": 0
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
                    print("Data: ",data)
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
                            action = self.go_to
                        elif data["command"] == "PAY":
                            action = self.pay
                        elif data["command"] == "CARD":
                            action = self.card
                        elif data["command"] == "START":
                            action = self.start
                        else:
                            action = self.broadcast_error
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
                    action = self.broadcast_error
                action(data, broadcastsock, address)
            except timeout:
                pass
            except Exception as e:
                print("Broadcast Error ",e)

    def broadcast_error(self, data, sock, address=None):
        # yes name is wrong... all errors go through here
        # {command:error}
        data = {"command": "ERROR",
                "values": "Unknown command"}
        self._send_answer(data, sock, address) if address != None else self._send_answer_tcp(data, sock)

    def _send_answer(self, data, sock, address):
        sock.sendto(dumps(data).encode(), address)
        print("Sent")

    def _send_answer_tcp(self,data, sock):
        sock.send(dumps(data).encode())
        print("Sent tcp")

    def _push_notification(self,data,exclude=None):
        for sock in self.game["comms"]:
            if sock != exclude:
                sock.send(dumps(data).encode())
                print("Sent notification")

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
        if len(self.game["players"]) < 6:
            self.game["comms"][self.game["top_id"]] = sock
            self.game["comms_rev"][sock] = self.game["top_id"]
            #add player to the player list
            self.game["players"].append(data["values"]["username"])
            self.game["top_id"] += 1
            #print("=" * 50)
            #print(self.game)
            #print("="*50)
            data = {
                "command": "CREATE",
                "values": "1",
            }
        else:
            data = {
                "command": "ERROR",
                "values": "Game already created try joining",
            }
        self._send_answer_tcp(data,sock)

    def poll_games(self, data, sock, address):
        # called by request handler <function=_handle_broadcast> when
        # incoming message has <var=command> = POLL
        # Returns: Game (ie. {"command": "GAME", "values": {"game":game_details}}
        data = {
            "command": "GAME",
            "values": {
                "game": {
                    "name": self.game["name"],
                    "players": [player for player in self.game["players"]]
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
            self.game["players"].append(data["values"]["username"])
            self.game["top_id"] += 1
            success = 1
        data = {
            "command": "JOIN",
            "values": success,
        }
        self._push_notification(data)


    """
    <-------------------- CLIENT TO SERVER ------------------------------>
        Following function get called buy requests from client or as
        "missing a word" to an action performed as a result of a request
    <-------------------------------------------------------------------->
    """
    def start(self,data, sock):
        if self.game["comms"][sock] == 0:
            if self.game["top_id"] >= 2:
                self.game["started"] = True
                data = {
                    "command": "START",
                    "values": {
                        "players": self.game["players"],
                    }
                }
            else:
                data = {
                    "command": "ERROR",
                    "values": "You can't play on your own."
                }
        else:
            data = {
                "command": "CHAT",
                "values": {
                    "text": "Start the game already!!",
                    "player": self.game["players"][self.game["comms"][sock]]
                }
            }
        self._push_notification(data,sock)

    def roll(self, data, sock):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = ROLL
        # generates two random numbers in range(1,7)
        # Returns: ROLL message
        data = {
            "command": "ROLL",
            "values":{
                "roll": [randint(1,7), randint(1,7)],
            }
        }
        self._send_answer_tcp(data,sock)
        #send goto to all other players
        self.go_to(data,sock)

    def buyRequest(self, data, sock):
        data = {
            "command": "BUY?",
            "vales": {}
        }
        self._send_answer_tcp(data, sock)

    def buy(self, data, sock):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = BUY
        # 'buys' the property that the player is currently on
        # Returns: Success / Failure message
        if data["values"]["buy"]:
            player_id = self.game["comms"][sock]
            player = self.game["board"].getPlayer(player_id)
            space_id = player.getPosition()
            space = self.game["board"].getSpace(space_id)
            if player.getBalance() > space.getPrice()
                player.addProperty(space)
                space.setOwner(player_id)
                out = {
                    "command": "BOUGHT",
                    "values": {
                        "player": player_id,
                        "tile": space_id
                    }
                }
                self._push_notification(out)

    def sell(self, data, sock):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = SELL
        # 'sells' the properties defined in <var=ids> inside <var=values>
        # Returns: PAY message
        player_id = self.game["comms"][sock]
        player = self.game["board"].getPlayer(player_id)
        total = 0
        sold = []
        for id in data["values"]["tiles"]:
            space = self.game["board"].getSpace(id)
            total += space.getPrice()
            if space.getOwner() == player_id:
                space.setOwner(None)
                sold += [id]
        out = {
                "command": "SOLD",
                "values": {
                    "tiles": sold,
                    "player": player_id
            }
        self._push_notification(out)

    def chat(self, data,sock):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = CHAT
        # Sends the message <var=text> that is in <var=values> onto other users,
        # attaching values like username onto the message
        # Returns: does not return just passes on ?? <-- NOTE * Not sure yet. * NOTE -->
        data = {
            "command": "CHAT",
            "values": {
                "text": data["text"],
                "from": self.game["comms"][sock].name
            }
        }
        self._push_notification(data,sock)

    def turn(self, data, sock):
        # send message TURN to all clients
        # informing them of whose turn it is
        data = {
            "command":"TURN",
            "values":{
                "player": self.game["turn"]
            }
        }
        self._push_notification(data)

    def go_to(self, data,sock):
        # inform all players where one player is
        # {values: {palyer: int player_id, tile: int tile } }
        data = {
            "command": "GOTO",
            "player": self.game["comms_rev"][sock],
            "tile": self._move_player(self.game["comms_rev"][sock], sum(data["values"]["roll"]))
        }
        self._push_notification(data)

    def _move_player(self,playerID, spaces):
        current_space = self.game["board"].getPlayer(playerID)
        if (current_space + spaces) > self.game["board"].getSize():
            new_space = (current_space + spaces) - self.game["board"].getSize()
        else:
            new_space = current_space + spaces
        return  new_space

    def pay(self, data, sock):
        # transaction between player and player or bank and player if
        # to or from are None
        # {"command": "PAY",
        #    "values": {
        #        "from": int player_id or None,
        #        "to": int player_id or None,
        #        "amount": int amount
        #     }
        # }
        if data["values"]["to"]:
            self.game["board"].getPlayer(data["values"]["to"]).addMoney(data["values"]["amount"])
        if data["values"]["from"]:
            self.game["board"].getPlayer(data["values"]["from"]).takeMoney(data["values"]["amount"])
        self. _push_notification(data)

    def card(self, tile):
        # Comunity Chest / Chance cards
        #
        # {
        #    "command": "CARD",
        #    "values": {
        #        "text": str text,
        #        "is_bail": bool is_bail
        #    }
        # }
        space = self.game["board"].getSpace(tile)
        card = space.drawCard()
        out = {
            "command": "CARD",
            "values": {
                "text": card.getText(),
                "is_bail": card.getType() == "BAIL"
            }
        }
        self._push_notification(out)
        return card


if __name__ == '__main__':
    Server()
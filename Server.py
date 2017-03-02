from socket import *
from json import dumps, loads
from threading import Thread, Timer
from random import randint
from select import select
from Board import Board
from StupidException import StupidException
from queue import Queue


class Server:

    BROADCAST_PORT = 44470
    SERVICE_PORT = 44469
    BOARD_FILE = "board.txt"
    CLIENT_DECISION_TIME = 60

    def __init__(self, broadcast_port=None, service_port=None):
        self._timeout = False
        self.connection_queue = Queue()
        self.timer = Timer(60, self.time)
        self.game = {
            "name": "Monopoly",
            "players": [],  # player names
            "comms": {},  # socket: id map
            "comms_rev": {},  # id: socket map
            "board": None,
            "top_id": 0,
            "started": False,
            "turn": 0,
            "last_action": {
                "rolled": False,
                "last_roll": [],
                "doubles": 0
            }
        }

        self.discover = Thread(target=self._open_broadcast,
                               args=(broadcast_port if broadcast_port is not None else Server.BROADCAST_PORT, ))
        self.discover.start()

        self.server = Thread(target=self._open_service,
                             args=((service_port if service_port is not None else Server.SERVICE_PORT), ))
        self.server.start()

    def _open_service(self, port):
        self.service_sock = socket()
        self.service_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.service_sock.bind(('', port))
        self.service_sock.listen(10)
        print("Service Listening")
        while True:
            try:
                connections, write, exception = select([self.service_sock], [], [], 0.05)
                for con in connections:
                    client_sock, address = con.accept()
                    data = loads(client_sock.recv(4096).decode())
                    print("Data: ", data)
                    try:
                        if data["command"] == "CREATE":
                            action = self.create_game
                        elif data["command"] == "JOIN":
                            action = self.join_game
                        elif data["command"] == "CHAT":
                            action = self.chat
                        elif data["command"] == "TURN":
                            action = self.turn
                        elif data["command"] == "START":
                            action = self.start
                        elif data["command"] == "QUIT":
                            action = self.quit
                        else:
                            self.connection_queue.put((data, client_sock))
                            raise StupidException("Skip action call")
                        action(data, client_sock)
                    except Exception as e:
                        print("TCP Error 1 ", e)
                        client_sock.close()
            except timeout:
                pass
            except StupidException:
                pass
            except Exception as e:
                print("TCP Error 2 ", e)

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
                print("Broadcast Error ", e)

    def broadcast_error(self, data, sock, address=None):
        # yes name is wrong... all errors go through here
        # {command:error}
        data = {"command": "ERROR",
                "values": "Unknown command"}
        self._send_answer(data, sock, address) if address else self._send_answer_tcp(data, sock)

    def _send_answer(self, data, sock, address):
        sock.sendto(dumps(data).encode(), address)
        print("Sent")

    def _send_answer_tcp(self,data, sock):
        sock.sendall(dumps(data).encode())
        print("Sent tcp")

    def _push_notification(self,data,exclude=None):
        for sock in self.game["comms_rev"]:
            if sock != exclude:
                sock.sendall(dumps(data).encode())
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
        if len(self.game["players"]) < 1:
            self.game["comms"][self.game["top_id"]] = sock
            self.game["comms_rev"][sock] = self.game["top_id"]
            # add player to the player list
            self.game["players"].append(data["values"]["username"])
            self.game["top_id"] += 1
            data = {
                "command": "CREATE",
                "values": "1"
            }
        else:
            data = {
                "command": "CREATE",
                "values": "0",
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
                    "name": None,
                    "players": None
                }
            }
        }
        if len(self.game["players"]) > 0:
            data["game"] = {
                "name": self.game["name"],
                "players": self.game["players"],
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
            print(">>>>JOIN : ", self.game["players"])
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
    def start(self, data, sock):
        if self.game["comms"][sock] == 0:
            if self.game["top_id"] >= 2:
                self.game["started"] = True
                self.game["board"] = Board(Server.BOARD_FILE, self.game["players"])
                data = {
                    "command": "START",
                    "values": {
                        "players": [{i, self.game["players"][i]} for i in range(len(self.game["players"]))],
                        "local": None,
                    }
                }
                for socket in self.game["comms"].keys():
                    data["values"]["local"] = self.game["comms"][socket]
                    self._send_answer_tcp(data,socket)
                self._playGame()
            else:
                data = {
                    "command": "ERROR",
                    "values": "You can't play on your own."
                }
                self._push_notification(data)
        else:
            data = {
                "command": "CHAT",
                "values": {
                    "text": "Start the game already!!",
                    "player": self.game["players"][self.game["comms"][sock]]
                }
            }
            self._push_notification(data, sock)

    def roll(self, data, sock):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = ROLL
        # generates two random numbers in range(1,7)
        # Returns: ROLL message
        data = {
            "command": "ROLL",
            "values": {
                "roll": [randint(1, 7), randint(1, 7)],
            }
        }
        self.game["last_action"]["rolled"] = True
        self.game["last_action"]["last_roll"] = data["values"]["roll"]
        self._push_notification(data)
        return data["values"]["roll"]

    def buyRequest(self, data, sock):
        data = {
            "command": "BUY?",
            "vales": {}
        }
        self._send_answer_tcp(data, sock)

    def _move_player(self,playerID, spaces):
        current_space = self.game["board"].getPlayer(playerID)
        if (current_space + spaces) > self.game["board"].getSize():
            new_space = (current_space + spaces) - self.game["board"].getSize()
            self.pass_go(self.game["comms_rev"][playerID])
        else:
            new_space = current_space + spaces
        return new_space

    def pass_go(self,sock):
        data = {
            "command": "PAY",
            "values": {
                "to": self.game["comms"][sock],
                "from": None,
                "amount": 200
            }
        }
        self.pay(data, sock)

    def _proccess_position(self, tile, sock):
        if tile == -1:
            tile = self.game["board"].getJailposition()

        board = self.game["board"]
        space = board.getSpace(tile)
        what = space.getType()

        if what == "DECK":

            space = space.drawCard()
            card = {
                "text":str(space),
                "is_bail": space.getValue(),
            }
            data = {"command": "CARD", "values": card}
            self._push_notification(data)
        if what == "GO":
            self.pass_go(sock)
        elif what == "PROPERTY":
            self._onPropertySpace(space,sock)
        elif what == "GOTOJAIL":
            self.sendJail(sock)
        elif what == "TAX" or what == "PAY":
            data = {"command": "PAY",
                    "values": {
                        "from": self.game["comms"][sock],
                        "to": None,
                        "amount": int(space.getValue())
                    }
            }
            self.pay(data,sock)
        elif what == "COLLECT":
            data = {"command": "PAY",
                    "values": {
                        "to": self.game["comms"][sock],
                        "from": None,
                        "amount": int(space.getValue())
                    }
            }
            self.pay(data, sock)
        elif what == "BAIL":
            data = {
                "command": "CARD",
                "values": {
                        "text": str(space),
                        "is_bail": True,
                    }
                }

            self._push_notification(data)
        elif what == "GOTO":
            where = space.getValue()
            data = {"values": {}}
            if where == "JAIL":
                self.sendJail(sock)
            elif where == "GO":
                data["values"]["tile"] = 0
            else:
                data["values"]["tile"] = where
            self.go_to(data,sock)
        else:
            pass #error

    def _waitResponse(self, command, sock):
        while not self._timeout:
            message = self.connection_queue.get()
            if message:
                if sock == message[1] and message[0]["command"] == command:
                    return message
        return "timeout"

    def _buy(self, space, player):
        player.addProperty(space)
        space.setOwner(player.getId())
        out = {
            "command": "BOUGHT",
            "values": {
                "player": player.getId(),
                "tile": space.getId()
            }
        }
        self._push_notification(out)


    def _onPropertySpace(self, space, sock):
        cost = int(space.getPrice())
        player_id = self.game["comms"][sock]
        owner_id = space.getOwner()
        player = self.game["board"].getPlayer(player_id)
        if (owner_id is not None) and (owner_id != player_id):
            # someone else owns the space so player pays them
            cost = int(space.getRent())
            data = {
                "command": "PAY",
                "values": {
                    "from": player_id,
                    "to": owner_id,
                    "ammount": cost
                }
            }
            self.pay(data, None)
        elif owner_id is None and player.getBalance() > cost:
            # send BUY?
            self.buyRequest(None, sock)
            # wait for response
            self.timer.start()
            out = self._waitResponse("BUY", sock)
            if out == "timeout":
                self._timeout = False
            else:
                if out[0]["values"]["buy"]:
                    data = {
                        "command": "PAY",
                        "values": {
                            "from": player.getId(),
                            "to": None,
                            "ammount": cost
                        }
                    }
                    self.pay(data, None)
                    self.buy(space, player)
        else:
            #future possability of buying houses if you land on that space??
            pass

    def remove_player(self, sock):
        pid = self.game["comms"][sock]
        self.game["comms"].pop(sock)
        self.game["comms_rev"].pop(pid)
        self.game["board"].removePlayer(pid)

    def quit(self, data, sock):
        data = {
            "command": "QUIT",
            "values": {"player": self.game["comms"][sock]}
        }
        self.remove_player(sock)
        self._push_notification(data,sock)

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

    def go_to(self, data, sock):
        # inform all players where one player is
        # {values: {palyer: int player_id, tile: int tile } }
        d = {
            "command": "GOTO",
            "values": {
                "player": self.game["comms_rev"][sock],
                "tile": None
            }
        }
        p = self.game["board"].getPlayer(self.game["comms"][sock])
        if "roll" in data["values"]:
            d["values"]["tile"] = self._move_player(self.game["comms_rev"][sock], sum(data["values"]["roll"]))
            p.setPosition(d["values"]["tile"])
        elif "jail" in data["values"]:
            d["values"]["tile"] = -1
            p.setPosition(self.game["board"].getJailPosition())
        else:
            d["values"]["tile"] = data["values"]["tile"]

        self._push_notification(d)
        self._proccess_position(d["tile"], sock)

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
            if space.getOwner() == player_id:
                space.setOwner(None)
                sold += [id]
                total += space.getPrice()
        out = {
                "command": "SOLD",
                "values": {
                    "tiles": sold,
                    "player": player_id
            }
        }
        self._push_notification(out)
        data = {
            "command": "PAY",
            "values": {
                "from": None,
                "to": player_id,
                "ammount": total
            }
        }
        self._push_notification(data)

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


    def sendJail(self, sock):
        pid = self.game["comms"][sock]
        data = {"command": "JAIL",
                "values": {
                    "player": pid
                    }
                }
        self._push_notification(data)
        self.game["board"].getPlayer(pid).updateJailed()

    def time(self):
        print("Timeout")
        self._timeout = True

    def _playGame(self):
        while True:
            try:
                if (not self.game["last_action"]["rolled"]) and (self.game["comms"][self.game["turn"]] is not None):
                    sentToJail = False
                    self.turn(None, None)
                    self.timer.start()
                    out = self._waitResponse("ROLL", self.game["comms"][self.game["turn"]])
                    if out == "timeout":
                        self._timeout = False
                        self.game["last_action"]["rolled"] = False
                        self.game["turn"] += 1
                        self.game["last_action"]["last_roll"] = []
                    else:
                        roll = self.roll({}, self.game["comms"][self.game["turn"]])
                        if roll[0] == roll[1]:
                            if self.game["last_action"]["doubles"] == 3:
                                self.sendJail(self.game["comms"][self.game["turn"]])
                                sentToJail = True
                                self.game["last_action"]["rolled"] = True
                            else:
                                self.game["last_action"]["rolled"] = False
                        else:
                            self.game["last_action"]["rolled"] = True
                        if not sentToJail:
                            data = {"command": "GOTO", "values": {"roll": roll}}
                            self.go_to(data, self.game["comms"][self.game["turn"]])
                        else:
                            data = {"command": "GOTO", "values": "JAIL"}
                            self.go_to(data, self.game["comms"][self.game["turn"]])
                else:
                    self.game["last_action"]["rolled"] = False
                    self.game["turn"] += 1
                    self.game["last_action"]["last_roll"] = []
            except Exception as e:
                print(e)

if __name__ == '__main__':
    Server()
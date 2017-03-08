from socket import *
from json import dumps, loads
from threading import Thread, Timer
from random import randint
from select import select
from Board import Board
from StupidException import StupidException
from queue import Queue
from time import sleep
import sys
import traceback


class Server:

    BROADCAST_PORT = 44470
    SERVICE_PORT = 44469
    BOARD_FILE = "text/full_board.txt"
    CLIENT_DECISION_TIME = 60
    GO_CASH = 50
    GETOUT = 200

    def __init__(self, broadcast_port=None, service_port=None):
        self._game_over = False
        self.incomming = False
        self._timeout = False
        self.connection_queue = Queue()
        self.timer = Timer(60, self.time)
        self.game = {
            "name": "Monopoly",
            "players": [],  # player names
            "socket_to_id": {},  # socket: id map
            "id_to_socket": {},  # id: socket map
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

        self.service = Thread(target=self._service,
                             args=((service_port if service_port is not None else Server.SERVICE_PORT), ))
        self.service.start()

    def _run_incomming(self):
        if not self.incomming:
            self.incomming_thread = Thread(target=self._incomming_messages,
                              args=())
            self.incomming_thread.start()

    def _incomming_messages(self,):
        while not self._game_over:
            try:
                connections, write, exception = select(list(self.game["socket_to_id"]), [], [], 0.05)
                for con in connections:
                    data = con.recv(4096).decode()
                    try:
                        data = loads(data)
                        self._enqueueMessage(data,con)
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
                                        message = loads(message)
                                        self._enqueueMessage(message,con)
                                    except ValueError:
                                        print("Invalid JSON string received: " + message)
                                    except Exception as e:
                                        traceback.format_exc()
            except timeout:
                pass
            except StupidException:
                pass
            except KeyboardInterrupt:
                return
            except Exception as e:
                print("TCP Error 2 ", e)
                return 0

    def _enqueueMessage(self,data,con):
        print("Data: ", data)
        try:
            if data["command"] == "CHAT":
                action = self.chat
            elif data["command"] == "TURN":
                action = self.turn
            elif data["command"] == "START":
                action = self.start
            elif data["command"] == "QUIT":
                action = self.quit
            else:
                self.connection_queue.put((data, con))
                raise StupidException("Skip action call")
            action(data, con)
        except Exception as e:
            print("TCP Error 1 ", e)
            # con.close()

    def _service(self,port):
        self.service_sock = socket()
        self.service_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.service_sock.bind(('', port))
        self.service_sock.listen(10)
        print("Service Listening")
        while not self._game_over:
            try:
                connections, write, exception = select([self.service_sock], [], [], 0.05)
                for con in connections:
                    client_sock, address = con.accept()
                    data = loads(client_sock.recv(4096).decode())
                    print("Data: ", data)
                    try:
                        if data["command"] == "JOIN":
                            action = self.join_game
                        elif data["command"] == "CREATE":
                            action = self.create_game
                        else:
                            raise StupidException("Skip action call")
                        action(data, client_sock)
                    except StupidException:
                        pass
                    except Exception as e:
                        print("TCP Error 1 ", e)
                        #con.close()
            except timeout:
                pass
            except StupidException:
                pass
            except KeyboardInterrupt:
                return
            except Exception as e:
                print("TCP Error 2 ", e)

    def _open_broadcast(self, broadcast_port):
        broadcastsock = socket(AF_INET, SOCK_DGRAM)
        broadcastsock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        broadcastsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        broadcastsock.bind(('', broadcast_port))
        broadcastsock.settimeout(1)
        print("Broadcast Ready")
        while not self._game_over:
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
            except KeyboardInterrupt:
                return
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
        for sock in self.game["socket_to_id"]:
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
            self.game["id_to_socket"][self.game["top_id"]] = sock
            self.game["socket_to_id"][sock] = self.game["top_id"]
            # add player to the player list
            self.game["players"].append(data["values"]["username"])
            self.game["top_id"] += 1
            data = {
                "command": "CREATE",
                "values": {"status":"1"},
            }
            self._run_incomming()
        else:
            data = {
                "command": "CREATE",
                "values": {"status":"1"},
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
                    "players": None,
                    "password": None,
                }
            }
        }
        if len(self.game["players"]) > 0:
            data["values"]["game"] = {
                "name": self.game["name"],
                "players": self.game["players"],
                "password": None
            }
        self._send_answer(data, sock, address)

    def join_game(self, data, sock):
        # called by request handler <function=_handle_broadcast> when
        # incoming message has <var=command> = JOIN
        # Returns: Success / Failure message
        success = "0"
        if not self.game["started"] and (self.game["top_id"] < 6 and self.game["top_id"] > 0 ):
            self.game["id_to_socket"][self.game["top_id"]] = sock
            self.game["socket_to_id"][sock] = self.game["top_id"]
            # add player to the player list
            self.game["players"].append(data["values"]["username"])
            self.game["top_id"] += 1
            success = "1"
            print(">>>>JOIN : ", self.game["players"])
            self._run_incomming()
        data = {
            "command": "JOIN",
            "values": {"status":success},
        }
        self._send_answer_tcp(data,sock)


    """
    <-------------------- CLIENT TO SERVER ------------------------------>
        Following function get called buy requests from client or as
        "missing a word" to an action performed as a result of a request
    <-------------------------------------------------------------------->
    """
    def start(self, data, sock):
        if self.game["socket_to_id"][sock] == 0:
            if self.game["top_id"] >= 2:
                self.game["started"] = True
                players = {i:self.game["players"][i] for i in range(len(self.game["players"]))}
                self.game["board"] = Board(Server.BOARD_FILE, players)
                data = {
                    "command": "START",
                    "values": {
                        "players": players,
                        "local": None,
                    }
                }
                for socket in self.game["socket_to_id"].keys():
                    data["values"]["local"] = self.game["socket_to_id"][socket]
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
                    "player": self.game["players"][self.game["socket_to_id"][sock]]
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
                "roll": [randint(1, 6), randint(1, 6)],
            }
        }
        self.game["last_action"]["rolled"] = True
        self.game["last_action"]["last_roll"] = data["values"]["roll"]
        self._send_answer_tcp(data,sock)
        return data["values"]["roll"]

    def buyRequest(self, data, sock):
        data = {
            "command": "BUY?",
            "values": {}
        }
        self._send_answer_tcp(data, sock)

    def _move_player(self,playerID, spaces):
        current_space = self.game["board"].getPlayer(playerID).getPosition()
        if (current_space + spaces) > self.game["board"].getSize():
            new_space = (current_space + spaces) - self.game["board"].getSize()
            self.pass_go(self.game["id_to_socket"][playerID])
        else:
            new_space = current_space + spaces
        return new_space

    def pass_go(self,sock):
        self.pay(None, self.game["socket_to_id"][sock], Server.GO_CASH, sock)

    def _handle_card(self, card, sock):
        card_text = card.getText()
        card_type = card.getType()
        data = {
            "command": "CARD",
            "values": {
                "text": card_text,
                "is_bail": (True if card_type == "BAIL" else False),
            }
        }
        self._push_notification(data)

        if card_type == "COLLECT":
            self.pay(None, self.game["socket_to_id"][sock], int(card.getValue()), sock)
        elif card_type == "PAY":
            self.pay(self.game["socket_to_id"][sock], None, int(card.getValue()), sock)
        elif card_type == "BAIL":
            self.game["board"].getPlayer(self.game["socket_to_id"][sock]).updateBail(True)
        elif card_type == "GOTO":
            where = card.getValue()
            data = {"values": {}}
            print(data, "where: ", where)
            if where == "JAIL":
                data["values"] = "JAIL"
                self.sendJail(sock)
            elif where == "GO":
                data["values"]["tile"] = 0
            else:
                data["values"]["tile"] = int(where)
            print("CARD SAYS GO TO",data)
            self.go_to(data, sock)



    def _proccess_position(self, tile, sock):
        print("process",1)
        board = self.game["board"]
        if tile == -1:
            what = "GOTOJAIL"
        else:
            space = board.getSpace(tile)
            what = space.getType()

        if what == "DECK":
            card = space.drawCard()
            self._handle_card(card,sock)
        elif what == "GO":
            self.pass_go(sock)
        elif what == "PROPERTY":
            print("process", 2)
            self._onPropertySpace(space,sock)
        elif what == "GOTOJAIL":
            self.sendJail(sock)
        elif what == "TAX":
            self.pay(self.game["socket_to_id"][sock], None, int(space.getFee()), sock)
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
                "tile": player.getPosition()
            }
        }
        self._push_notification(out)


    def _onPropertySpace(self, space, sock):
        cost = int(space.getPrice())
        player_id = self.game["socket_to_id"][sock]
        owner_id = space.getOwner()
        player = self.game["board"].getPlayer(player_id)
        if (owner_id is not None) and (owner_id != player_id):
            # someone else owns the space so player pays them
            cost = int(space.getRent())
            self.pay(player_id, owner_id, cost, sock)
        elif owner_id is None and player.getBalance() > cost:
            # send BUY?
            self.buyRequest(None, sock)
            # wait for response
            #self.timer.start()
            out = self._waitResponse("BUY", sock)
            if out == "timeout":
                self._timeout = False
            else:
                print("On property response:", out)
                if out[0]["values"]["buy"]:
                    self.pay(player_id, None, cost, sock)
                    self._buy(space, player)
        else:
            #future possability of buying houses if you land on that space??
            pass

    def remove_player(self, sock):
        pid = self.game["socket_to_id"][sock]
        self.game["socket_to_id"].pop(sock)
        self.game["id_to_socket"].pop(pid)
        self.game["board"].removePlayer(pid)

    def quit(self, data, sock):
        data = {
            "command": "QUIT",
            "values": {"player": self.game["socket_to_id"][sock]}
        }
        self.remove_player(sock)
        self._push_notification(data,sock)

    def chat(self, data,sock):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = CHAT
        # Sends the message <var=text> that is in <var=values> onto other users,
        # attaching values like username onto the message
        # Returns: does not return just passes on ?? <-- NOTE * Not sure yet. * NOTE -->
        print("Sending chat",data)
        message = data["values"]["text"]
        sender = None
        if sock:
            sender = self.game["board"].getPlayer(self.game["socket_to_id"][sock]).getName()
        data = {
            "command": "CHAT",
            "values": {
                "player": sender,
                "text": data["values"]["text"]
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
        print(data)
        self._push_notification(data)

    def go_to(self, data, sock):
        # inform all players where one player is
        # {values: {palyer: int player_id, tile: int tile } }
        player_id = self.game["socket_to_id"][sock]
        jail = False
        d = {
            "command": "GOTO",
            "values": {
                "player": player_id,
                "tile": None
            }
        }
        p = self.game["board"].getPlayer(player_id)
        if "roll" in data["values"]:
            d["values"]["tile"] = self._move_player(player_id, sum(data["values"]["roll"]))
            p.setPosition(d["values"]["tile"])
        elif "JAIL" in data["values"]:
            jail = True
            d["values"]["tile"] = self.game["board"].getJailPosition()
            p.setPosition(d["values"]["tile"])
        else:
            print("GO TO DATA:",data)
            d["values"]["tile"] = data["values"]["tile"]
            p.setPosition(d["values"]["tile"])
        self._push_notification(d)
        if not jail:
            self._proccess_position(d["values"]["tile"], sock)
        else:
            self._proccess_position(-1, sock)

    def pay(self,p_from,p_to,amount,sock):
        # transaction between player and player or bank and player if
        # to or from are None
        # {"command": "PAY",
        #    "values": {
        #        "from": int player_id or None,
        #        "to": int player_id or None,
        #        "amount": int amount
        #     }
        # }
        data = {"command": "PAY",
                "values": {
                    "player_from": p_from,
                    "player_to": p_to,
                    "amount": amount
                }
                }
        if p_to is not None:
            self.game["board"].getPlayer(p_to).addMoney(amount)
        if p_from is not None:
            self.game["board"].getPlayer(p_from).takeMoney(amount)
        self. _push_notification(data)


    def sell(self, data, sock):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = SELL
        # 'sells' the properties defined in <var=ids> inside <var=values>
        # Returns: PAY message
        player_id = self.game["socket_to_id"][sock]
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


    def sendJail(self, sock):
        pid = self.game["socket_to_id"][sock]
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

    def gameOver(self, players):
        #self.discover.join()
        data = {"command": "CHAT", "values": {"text": "Player " + str(players[0]) + "wins" if len(players) < 2 else "Draw"}}
        self.chat(data,None)
        data = {"command": "GAMEOVER"}
        self._push_notification(data)
        print("sent game over message",data)
        self._game_over = True
        sleep(5)
        self.__init__()



    def _playGame(self):
        while True:
            print("game x")
            current_turn_sock = self.game["id_to_socket"][self.game["turn"]]
            print(self.game["board"].getPlayer(self.game["turn"])," : ",self.game["board"].getPlayer(self.game["turn"]).isBankrupt())
            try:
                count_not_bankrupt = []
                for player in self.game["board"].getPlayerList():
                    if not player.isBankrupt():
                        print(1)
                        count_not_bankrupt += [player]
                if len(count_not_bankrupt) < 2:
                    print("GAME OVER")
                    self.gameOver(count_not_bankrupt)
                    break
                if (not self.game["last_action"]["rolled"]) and (current_turn_sock is not None) and (not self.game["board"].getPlayer(self.game["turn"]).isBankrupt()) :
                    print("game y")
                    sentToJail = False
                    self.turn(None, None)
                    #self.timer.start()
                    out = self._waitResponse("ROLL", current_turn_sock)
                    if out == "timeout":
                        print("timed out waiting for roll")
                        self._timeout = False
                        self.game["last_action"]["rolled"] = False
                        self.game["turn"] += 1
                        self.game["last_action"]["last_roll"] = []
                    else:
                        print("game z")
                        roll = self.roll({}, current_turn_sock)
                        if roll[0] == roll[1]:
                            if self.game["board"].getPlayer(self.game["turn"]).isJailed():
                                self.game["board"].getPlayer(self.game["turn"]).updateJailed()
                            if self.game["last_action"]["doubles"] == 3:
                                self.sendJail(current_turn_sock)
                                sentToJail = True
                                self.game["last_action"]["rolled"] = True
                            else:
                                self.game["last_action"]["rolled"] = False
                                self.game["last_action"]["doubles"] += 1
                        else:
                            if self.game["board"].getPlayer(self.game["turn"]).isJailed():
                                self.pay(self.game["turn"], None, Server.GETOUT, None)
                                self.game["board"].getPlayer(self.game["turn"]).updateJailed()
                            self.game["last_action"]["rolled"] = True
                        if not sentToJail:
                            print("prepping a goto")
                            data = {"command": "GOTO", "values": {"roll": roll}}
                            self.go_to(data, current_turn_sock)
                        else:
                            data = {"command": "GOTO", "values": "JAIL"}
                            self.go_to(data, current_turn_sock)
                else:
                    print("game z")
                    self.game["last_action"]["rolled"] = False
                    self.game["turn"] += 1
                    if self.game["turn"] == self.game["top_id"]:
                        self.game["turn"] = 0
                    self.game["last_action"]["last_roll"] = []
            except Exception as e:
                print("Exception .... WTF???       ",traceback.print_exc(),e)

if __name__ == '__main__':
    Server()

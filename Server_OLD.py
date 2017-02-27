from socket import *
from json import dumps, loads
from threading import Thread
from random import randint
#
# Discovery on port 44445
# All other messages on port 6969
#


class Server:
    def __init__(self):
        """/*
        Port on which the the server is running
        */"""
        self.port = 6969
        self.game_id = 0
        self.double_roll = 0
        self.started_games = {}  # ongoing games, {game_id: [players]}
        #          where player a dictionary of {playerName : address}
        self.open_games = {}  # games that can be joined, {game_id: [players]}
        #                  where player a dictionary of {playerName : address}
        self.boards_data = {}  # {game_id: Board}
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("", self.port))
        self.started = False
        self.discover = Thread(target=self.enable_discovery)
        self.discover.start()

    def enable_discovery(self):
        """Allow clients to discover the server"""
        broadcastSock = socket(AF_INET, SOCK_DGRAM)
        broadcastSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        broadcastSock.bind(('', 44445))
        broadcastSock.settimeout(1)
        print('Starting up broadcast service')
        while True:
            try:
                data, address = broadcastSock.recvfrom(1024)
                data = loads(data.decode())
                if data["command"] == "open_games_request":
                    data = {
                        'games': self.open_games
                    }
                elif data["command"] == "create_game_request":
                    self.open_games[self.game_id] = {data["player_name"]: address}
                    data = {
                        'game_id': self.game_id
                    }
                    self.game_id += 1
                elif data["command"] == "join":
                    if (data["game_id"] in self.open_games) and (len(self.open_games[data["game_id"]]) < 6):
                        print("Keys : " + str(self.open_games[data["game_id"]].keys()))
                        if data["player_name"] not in self.open_games[data["game_id"]].keys():
                            self.open_games[data["game_id"]][data["player_name"]] = address
                        data = {
                            "game_id": data["game_id"],
                            "game_state": self.open_games[data["game_id"]]

                        }
                else:
                    data = {
                        'error': 'invalid request'
                    }
                serverState = {
                    'port': self.port,
                    'data': data
                }
                broadcastSock.sendto(dumps(serverState).encode(), address)
            except timeout:
                pass
            except Exception as e:
                print("Something went wrong")
                print(e)

    def recieve_messages(self):
        recieveSock = socket(AF_INET, SOCK_DGRAM)
        recieveSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        recieveSock.bind('', self.port)
        while True:
            try:
                data, address = recieveSock.revcfrom(1024)
                if data:
                    self.process_messages(data, address)
            except timeout:
                pass

    def process_messages(self, data, address):
        data = loads(data.decode())
        try:
            if self.started_games[data["game_id"]][data["player_name"]] == address:
                # request from a vaild player
                """
                Perform command based on the rest of the message
                """
                if data["command"] == "ROLL":
                    values = self.roll()
                    if values[1] == values[0]:
                        self.double_roll += 1
                    else:
                        self.double_roll = 0
                    data = {
                        "command": "ROLL",
                        "values" : values
                    }
                elif data["command"] == "BUY":
                    # get the square on which the player is and
                    pass
                elif data["command"] == "SELL":
                    pass
        except Exception as e:
            print(e)

    def roll(self):
        return [randint(1, 7), randint(1, 7)]
if __name__ == '__main__':
    Server()

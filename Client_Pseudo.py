import socket
import json
s1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s1.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
def f(s,dictionary):
    data = json.dumps(dictionary)
    s.sendto(data.encode(),("255.255.255.255",44445))
    data = None
    while data == None:
        data, addr = s.recvfrom(1024)
        data = json.loads(data.decode())
        print(data)

f(s1, {"action": "open_games_request"})
f(s1, {"action": "create_game_request", "player_name": "player1"})
f(s2, {"action": "open_games_request"})
f(s2, {"action": "join", "player_name": "player2", "game_id": 0})
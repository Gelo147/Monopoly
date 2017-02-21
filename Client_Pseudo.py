import socket
import json
from select import select

class TestServer:
    b_port = 44470
    t_port = 44469

    def test_broadcast(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
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

    def test_create(self):
        s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s1.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s2 = socket.socket()
        poll = json.dumps({"command": "POLL"})
        s1.sendto(poll.encode(), ("255.255.255.255", 44470))
        data = None
        while data == None:
            data, addr = s1.recvfrom(1024)
            s2.connect((addr[0], 44469))
            data = json.loads(data.decode())
            print(data)
        data = json.dumps(({"command": "CREATE", "values": {"username": "player1"}}))
        s2.sendall(data.encode())
        poll = json.dumps({"command": "POLL"})
        s1.sendto(poll.encode(), ("255.255.255.255", 44470))
        print("sent poll")
        data = None
        while data == None:
            data, addr = s1.recvfrom(1024)
            data = json.loads(data.decode())
            print(data)
        data = json.dumps(({"command": "CREATE", "values": {"username": "player1"}}))
        s2.sendall(data.encode())
        data = None
        while data == None:
            try:
                connections, write, exception = select([s2], [], [], 0.05)
                for con in connections:
                    client_sock, address = con.accept()
                    data = loads(client_sock.recv(4096).decode())
                    print(data)
            except timeout:
                pass
        s1.close()
        s2.close()
x = TestServer()
x.test_create()
"""
s1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s1.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s2 = socket.socket()
s3 = socket.socket()
addr = None
def broadcast(s,dictionary,t=True):
    data = json.dumps(dictionary)
    s.sendto(data.encode(),("255.255.255.255",44470))
    data = None
    while data == None:
        data, addr = s.recvfrom(1024)
        if t:
            s2.connect((addr[0],44469))
        data = json.loads(data.decode())
        print(data)

def tcp(data):
    s2.sendall(json.dumps(data).encode())

broadcast(s1, {"command": "POLL"})
tcp({"command": "CREATE", "values": {"username": "player1"}})
broadcast(s1, {"command": "POLL"},False)
#tcp(s2, {"command": "JOIN", "player_name": "player2", "game_id": 0})

s1.close()
s2.close()
"""
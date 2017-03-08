from json import dumps, loads
from socket import *
from sys import stdout, exc_info
from threading import Thread, Timer

from .Server import Server


class TestClient(socket):

    def __init__(self):
        super(TestClient, self).__init__()
        while True:
            try:
                self.connect(('', 44469))
                break
            except:
                pass

    def send_create(self, username='Guest', password=None):
        msg = dumps({'command': 'CREATE', 'values': {'game': 'Monopoly', 'username': username, 'password': password}})
        self.sendall(msg.encode())

    def send_join(self, username='', password=None):
        msg = dumps({'command': 'JOIN', 'values': {'game': 'Monopoly', 'username': username, 'password': password}})
        self.sendall(msg.encode())

    def send_start(self):
        msg = dumps({'command': 'START', 'values': {}})
        self.sendall(msg.encode())

    def send_roll(self):
        msg = dumps({'command': 'ROLL', 'values': {}})
        self.sendall(msg.encode())

    def send_buy(self, buy=True):
        msg = dumps({'command': 'BUY', 'values': {'buy': int(buy)}})
        self.sendall(msg.encode())

    def send_chat(self, message):
        msg = dumps({'command': 'CHAT', 'values': {'text': message}})
        self.sendall(msg.encode())

    def send_end(self):
        msg = dumps({'command': 'END', 'values': {}})
        self.sendall(msg.encode())


def run_game(sock: TestClient, pid: int):
    turn = False
    end_timer = Timer(2, sock.send_end)
    while True:
        try:
            data = sock.recv(4096).decode()
            messages = data.split('}{')
            if len(messages) > 1:
                messages[0] += '}'
                messages[-1] = '{' + messages[-1]
                for i in range(1, len(messages) - 1):
                    messages[i] = '{' + messages[i] + '}'
            else:
                messages = [data]
            for message in messages:
                data = loads(message)
                # Do some checks
                if data['command'] == 'CHAT' and pid == 0:
                    stdout.write('%s > %s\n' % (data['values']['player'], data['values']['text']))
                elif data['command'] == 'TURN':
                    if data['values']['player'] == pid:
                        turn = True
                        stdout.write("Player %i> It's my turn\n" % (pid + 1))
                        sock.send_roll()
                elif data['command'] == 'BUY?':
                    sock.send_buy(True)
                elif data['command'] == 'GAMEOVER':
                    break
                elif data['command'] == 'ROLL' and data['values']['roll'][0] == data['values']['roll'][1]:
                    stdout.write('Player %i> Rolled Doubles\n' % (pid + 1))
                    Timer(2, sock.send_roll).start()
                else:
                    if turn:
                        turn = False
                        end_timer.cancel()
                        end_timer = Timer(4, sock.send_end)
                        end_timer.start()
                    else:
                        # Just ignore the message
                        pass
        except:
            stdout.write("%i got exception %s\n" % (pid, str(exc_info())))
            break
    return


def run_test():
    server = Server()
    thread = Thread(target=server.serve)
    thread.start()

    # Create the test clients
    player1 = TestClient()
    player2 = TestClient()

    # Create the server
    player1.send_create('Player 1')
    assert player1.recv(4096).decode() == '1'

    # Join the server
    player2.send_join('Player 2')
    assert player2.recv(4096).decode() == '1'

    # Start the game
    player1.send_start()
    assert loads(player1.recv(4096).decode()).get('command', None) == 'START'
    assert loads(player2.recv(4096).decode()).get('command', None) == 'START'

    t1 = Thread(target=run_game, args=(player1, 0))
    t1.start()
    t2 = Thread(target=run_game, args=(player2, 1))
    t2.start()

    t1.join()
    t2.join()
    print('Test Finished. Closing')
    player1.close()
    player2.close()
    server.end_game()


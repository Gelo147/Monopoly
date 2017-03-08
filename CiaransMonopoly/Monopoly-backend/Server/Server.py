from datetime import datetime
from json import dumps, loads
from select import select
from socket import *
from sys import exit, stderr, stdout
from threading import Thread

# Local imports
try:
    from .Card import Card
except SystemError:
    stderr.write('Monopoly.Server [ERROR]: Server must be run as a module. Check the README for instructions')
    exit(1)
# Safe to assume all other local imports will pass
from .Player import Player
from .Board import Board


class Server:

    # The max number of players allowed in the lobby
    _MAX_PLAYERS = 8

    # The max wait for the 'select' methods
    _SELECT_TIMEOUT = 0.05

    def __init__(self):
        # Set up variables
        self._log("Server starting up at " + gethostbyname(gethostname()))

        # Map of Player objects to sockets
        self._player_sockets = {}

        # Reverse map of sockets to Player objects
        self._socket_owners = {}

        # Instance of Board class
        self._board = Board(self)

        # Main socket port
        self._main_port = 44469

        # Main socket
        main_sock = socket()
        main_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            main_sock.bind(('', self._main_port))
        except OSError:
            self._log('Could not bind main socket to port 44469. Is there a Monopoly Server already running?')
            exit(1)
        self._main_sock = main_sock

        # Polling socket port
        self._poll_port = 44470

        # Polling socket
        poll_sock = socket(AF_INET, SOCK_DGRAM)
        poll_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        poll_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            poll_sock.bind(('', self._poll_port))
        except OSError:
            self._log('Could not bind polling socket to port 44470. Is there a Monopoly Server already running?')
            exit(1)

        self._poll_sock = poll_sock

        # Password
        self._password = None

        # Created
        self._created = False

        # Started
        self._started = False

        # Serving
        self._serving = False

        # Closed
        self._closed = False

        # Finished
        self._finished = False

        # Polling Thread
        self._polling_thread = Thread(target=self._poll_listener, daemon=True)

        # Main Thread
        self._main_thread = Thread(target=self._create_listener)

    def serve(self) -> None:
        if not self._serving:
            self._main_thread.start()
            self._serving = True
            self._main_thread.join()
        else:
            self._log('Server.serve has already been called, the server is serving', stderr)

    def close(self) -> None:
        # Cleanup
        self._log("Server Closing")
        self._closed = True
        self._main_sock.close()
        self._poll_sock.close()

    def end_game(self) -> None:
        # End the game after a winner has been chosen
        # Will end loop in self._main_listener, which will then call self.close
        msg = self._generate_message('GAMEOVER')
        self._send_to_all(msg)
        self._finished = True

    """
        Listeners
    """

    def _create_listener(self) -> None:
        # Have the main socket listen for CREATE messages
        self._main_sock.listen(10)
        self._log("Server awaiting valid CREATE message")

        try:
            while not self._created:
                if self._closed:
                    break
                connections, w, x = select([self._main_sock], [], [], Server._SELECT_TIMEOUT)

                for conn in connections:
                    client_sock, address = conn.accept()
                    message = client_sock.recv(4096).decode()
                    try:
                        data = loads(message)
                        # Check that the command is correct
                        if 'command' not in data or data['command'] != 'CREATE':
                            raise ValueError()
                        # Check for the necessary data, knowing the command is correct
                        if 'values' not in data or 'game' not in data['values'] or data['values']['game'] != 'Monopoly':
                            raise ValueError()

                        # Game Creation message obeys API for now, so try to get the necessary data
                        # Password will either be None or an encrypted text
                        self._password = data['values'].get('password', None)

                        # Create a Player object with a unique id with this username
                        username = data['values'].get('username', 'Guest')
                        player = Player(username)

                        # Send the player to the Board
                        self._board.add_player(player)

                        # Store the player socket
                        self._player_sockets[player] = client_sock
                        self._socket_owners[client_sock] = player

                        # Inform the client of success
                        client_sock.sendall('1'.encode())

                        # Don't close client_sock since we'll be using it to communicate with the client

                        # Set _created to True to escape loop
                        self._created = True
                    except ValueError:
                        self._log('Invalid CREATE payload received: ' + message, stderr, 'WARN')
                        client_sock.sendall('0'.encode())
                        client_sock.close()

            # Open the server
            if self._created:
                self._log("Valid CREATE received. Server opening")
                self._pre_game_listen()

        except Exception as e:
            self._log("Closing due to exception: " + str(e), stderr)
            self.close()

        finally:
            return

    def _pre_game_listen(self) -> None:
        # Open the polling socket
        self._polling_thread.start()

        # Make the main socket listen for new things
        self._main_thread = Thread(target=self._start_listener)
        self._main_thread.start()
        self._join_listener()

    def _poll_listener(self) -> None:
        # Listen for POLL requests
        while not self._started:
            if self._closed:
                break
            try:
                data, addr = self._poll_sock.recvfrom(4096)
                data = data.decode()
                data = loads(data)
                # Check for matching API
                # Check for command value
                if 'command' not in data or data['command'] != 'POLL':
                    raise ValueError()

                # Check for values
                if 'values' not in data or 'game' not in data['values'] or data['values']['game'] != 'Monopoly':
                    raise ValueError()

                # If it reached this point, construct and send server data
                msg = self._generate_message(
                    'GAME',
                    password=self._password is not None,
                    players=[p.getUsername() for p in self._player_sockets]
                )
                # Send the game data back to the person asking
                self._poll_sock.sendto(msg.encode(), addr)

            except ValueError:
                self._log('Invalid POLL payload received: ' + data, stderr, 'WARN')
                self._poll_sock.sendto('0'.encode(), addr)
            except OSError:
                break
        return

    def _join_listener(self) -> None:
        """
        Listens for join requests
        """

        # Check for valid values
        while not self._started:
            if self._closed:
                break
            connections, w, x = select([self._main_sock], [], [], Server._SELECT_TIMEOUT)

            for conn in connections:
                client_sock, address = conn.accept()
                message = client_sock.recv(4096).decode()
                try:
                    data = loads(message)

                    if 'command' not in data or data['command'] != 'JOIN':
                        raise ValueError()

                    values = data['values']
                    if 'game' not in values or values['game'] != 'Monopoly':
                        raise ValueError()
                    if 'password' not in values or values['password'] != self._password:
                        raise ValueError()
                    # Check if lobby is full
                    if len(self._player_sockets) == Server._MAX_PLAYERS:
                        raise ValueError()

                    # At this point it's safe to say the JOIN request is valid
                    username = values.get('username', 'Guest')
                    player = Player(username)

                    # Send the player to the Board
                    self._board.add_player(player)

                    # Store the player socket
                    self._player_sockets[player] = client_sock
                    self._socket_owners[client_sock] = player

                    # Inform the client of success
                    client_sock.sendall('1'.encode())

                except ValueError:
                    self._log('Invalid JOIN payload received: ' + message, stderr, 'WARN')
                    client_sock.sendall('0'.encode())
                    client_sock.close()

    def _start_listener(self) -> None:
        """
        Listens for start request
        """

        # Check for valid values
        while not self._started:
            if self._closed:
                break
            client_sockets = self._socket_owners.keys()
            connections, w, x = select(client_sockets, [], [], Server._SELECT_TIMEOUT)

            for conn in connections:
                message = conn.recv(4096).decode()
                try:
                    data = loads(message)

                    if 'command' not in data or data['command'] != 'START':
                        raise ValueError()

                    # Check the number of players in game, should be >= 2
                    if len(self._player_sockets) >= 2:
                        # Start the game
                        # Send start messages to everybody
                        msg = {
                            'command': 'START',
                            'values': {
                                'players': {player.getId(): player.getUsername() for player in self._player_sockets}
                            }
                        }
                        for sock, player in self._socket_owners.items():
                            msg['values']['local'] = player.getId()
                            sock.sendall(dumps(msg).encode())
                        self._started = True
                    else:
                        raise AttributeError()

                except ValueError:
                    self._log('Invalid START payload received: ' + message, stderr, 'WARN')
                    conn.sendall('0'.encode())
                except AttributeError:
                    self._log('START Request was received without enough players', stderr, 'WARN')
                    conn.sendall('0'.encode())

        if not self._closed:
            self._log("Game starting")
            self._board.start()
            self._main_thread = Thread(target=self._main_listener)
            self._main_thread.start()

    def _main_listener(self) -> None:
        """
        The main listener for the game itself
        """
        while not self._finished:
            if self._closed:
                break
            # Await connections
            client_sockets = self._socket_owners.keys()
            connections, w, x = select(client_sockets, [], [], Server._SELECT_TIMEOUT)

            for conn in connections:
                message = ''
                try:
                    player = self._socket_owners[conn]
                    message = conn.recv(4096).decode()
                    data = loads(message)
                    Thread(target=self._handle_game_message, args=(data, player), daemon=True).start()
                except ValueError:
                    if message:
                        if len(message.split('}{')) == 1:
                            self._log("Invalid JSON string received: " + message, stderr, "WARN")
                        else:
                            self._log("Combined JSON payloads received: " + message, stderr, "WARN")
                            messages = message.split('}{')
                            messages[0] += '}'
                            messages[-1] = '{' + messages[-1]
                            for i, payload in enumerate(messages[1: -1], 1):
                                messages[i] = '{' + payload + '}'
                            for message in messages:
                                try:
                                    message = loads(message)
                                    Thread(
                                        target=self._handle_game_message,
                                        args=(message, player),
                                        daemon=True
                                    ).start()
                                except ValueError:
                                    self._log("Invalid JSON string received: " + message, stderr, "WARN")

                except KeyError:
                    self._log("Received message from unknown socket", stderr, "WARN")
                except ConnectionResetError:
                    # Remove the player
                    player = self._socket_owners[conn]
                    self._socket_owners.pop(conn)
                    self._player_sockets.pop(player)

        if not self._closed:
            self.close()

    def _handle_game_message(self, payload, player) -> None:
        try:
            # Run through all the possible api commands and run the appropriate function
            if 'command' not in payload:
                raise ValueError()

            command = payload['command']

            if command == 'ROLL':
                self._board.handle_roll(player)
            elif command == 'BUY':
                if payload['values']['buy'] == 1:
                    self._board.handle_buy(player)
            elif command == 'SELL':
                # Not implemented yet
                pass
            elif command == 'CHAT':
                text = payload['values']['text']
                self.send_chat(player, text)
            elif command == 'END':
                self._board.handle_end(player)
            else:
                raise ValueError()

        except (ValueError, KeyError):
            self._log("Invalid game command received: " + payload, stderr, "WARN")

    """
        Message Sending Methods
    """

    def send_turn(self, player: Player) -> None:
        # Constructs and sends a TURN message
        msg = self._generate_message('TURN', player=player.getId())
        self._send_to_all(msg)

    def send_roll(self, player: Player, dice: list) -> None:
        msg = self._generate_message('ROLL', roll=dice)
        sock = self._player_sockets[player]
        sock.sendall(msg.encode())

    def send_buy_request(self, player: Player) -> None:
        msg = self._generate_message('BUY?')
        sock = self._player_sockets[player]
        sock.sendall(msg.encode())

    def send_bought(self, player: Player, tile: int) -> None:
        msg = self._generate_message('BOUGHT', player=player.getId(), tile=tile)
        self._send_to_all(msg)

    def send_sold(self, player: Player, tiles: list) -> None:
        msg = self._generate_message('SOLD', player=player.getId(), tiles=tiles)
        self._send_to_all(msg)

    def send_goto(self, player: Player, tile: int) -> None:
        # Constructs and sends a GOTO message
        msg = self._generate_message('GOTO', player=player.getId(), tile=tile)
        self._send_to_all(msg)

    def send_jailed(self, player: Player) -> None:
        """
        Informs all clients that a player has been sent to or freed from jail
        :param player: The player who is entering or leaving jail
        """
        msg = self._generate_message('JAIL', player=player.getId())
        self._send_to_all(msg)

    def send_pay(self, amount: int, player_from: Player or None=None, player_to: Player or None=None) -> None:
        # Constructs and sends a PAY message
        try:
            if player_from is None and player_to is None:
                raise ValueError()
            msg = self._generate_message(
                'PAY',
                amount=amount,
                player_from=player_from.getId() if player_from is not None else None,
                player_to=player_to.getId() if player_to is not None else None)
            self._send_to_all(msg)
        except ValueError:
            self._log('Tried to PAY from the bank to the bank', stderr, 'WARN')

    def send_card(self, card: Card) -> None:
        # Constructs and sends a CARD message
        msg = self._generate_message('CARD', text=card.getText(), is_bail=card.isBail())
        self._send_to_all(msg)

    def send_quit(self, player: Player) -> None:
        msg = self._generate_message('QUIT', player=player.getId())
        self._send_to_all(msg)

    def send_event(self, event_message: str) -> None:
        # Sends an event message through the CHAT feature
        self.send_chat(None, event_message)

    def send_chat(self, player: Player or None, message: str) -> None:
        # Send a chat message from 'player'
        msg = self._generate_message('CHAT', player=player, text=message)
        self._send_to_all(msg)

    def _send_to_all(self, msg: str) -> None:
        # Sends 'message' to all players in game
        msg = msg.encode()
        for sock in self._socket_owners:
            sock.sendall(msg)

    @staticmethod
    def _generate_message(command: str, **values: dict) -> str:
        # Returns a message dumped with the passed command and values
        return dumps(
            {
                'command': command,
                'values': values
            }
        )

    @staticmethod
    def _log(msg: str, out=stdout, level=None) -> None:
        if level is None:
            level = 'INFO' if out is stdout else 'ERROR'
        time = datetime.now().strftime('%H:%M:%S.%f')
        output = '(%s) Monopoly.Server [%s]: %s\n' % (time, level, msg)
        out.write(output)

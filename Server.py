from socket import *
from json import dumps, loads
from threading import Thread
from random import randint


class Server:
    BROADCAST_PORT = 44470
    SERVICE_PORT = 44469

    def __init__(self, broadcast_port=Server.BROADCAST_PORT, service_port = Server.SERVICE_PORT):
        # Make the broadcast a separate thread
        self._openBroadcast(broadcast_port)
        self._openService(service_port)

    """
    <-------------------- CLIENT TO SERVER ------------------------------>
        Following function get called buy requests from client or as
        "missing a word" to an action performed as a result of a broadcast
    <-------------------------------------------------------------------->
    """
    def create_game(self, values, address):
        # called by request handler <function=_handle_broadcast> when
        # incoming message has <var=command> = CREATE
        # Returns: Success / Failure message
        pass

    def poll_games(self, values, address):
        # called by request handler <function=_handle_broadcast> when
        # incoming message has <var=command> = POLL
        # Returns: Game (ie. {"command": "GAME", "values": {"game":game_details}}
        pass

    def join_game(self, values, address):
        # called by request handler <function=_handle_broadcast> when
        # incoming message has <var=command> = JOIN
        # Returns: Success / Failure message
        pass

    """
    <-------------------- CLIENT TO SERVER ------------------------------>
        Following function get called buy requests from client or as
        "missing a word" to an action performed as a result of a request
    <-------------------------------------------------------------------->
    """

    def roll(self, values, address):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = ROLL
        # generates two random numbers in range(1,7)
        # Returns: ROLL message
        pass

    def buy(self, values, address):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = BUY
        # 'buys' the property that the player is currently on
        # Returns: Success / Failure message
        pass

    def sell(self, values, address):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = SELL
        # 'sells' the properties defined in <var=ids> inside <var=values>
        # Returns: PAY message
        pass

    def chat(self, values, address):
        # called by request handler <function=_handle_request> when
        # incoming message has <var=command> = CHAT
        # Sends the message <var=text> that is in <var=values> onto other users,
        # attaching values like username onto the message

        # Returns: does not return ?? <-- NOTE * Not sure yet. * NOTE -->
        pass

    def turn(self):
        # send message TURN to all clients
        # informing them of whose turn it is
        # <-- NOTE * self invoked sometimes?? * NOTE -->
        pass

    def go_to(self):
        # inform all players where one player is
        # {values: {palyer: int player_id, tile: int tile } }
        pass

    def pay(self):
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

    def card(self):
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

from Space import Space
from PropertySpace import PropertySpace
from TaxSpace import TaxSpace
from DeckSpace import DeckSpace
from Card import Card
from Player import Player
import random


class Board:
    """The representation of the game board where most of the action takes place"""

    def __init__(self, filename, playernames):
        # takes in a text file describing every space and a dictionary of player names to ids
        self._vaildtypes = ["GO", "PROPERTY", "JAIL", "FREE", "GOTOJAIL", "DECK", "TAX"]
        self._vaildcardtypes = ["COLLECT", "BAIL", "PAY", "GOTO"]
        self._property_sets = {}
        self._spaces = self._makeSpaces(filename)
        self._players = []
        self._jail_pos = 0
        for playername in playernames:
            print("Player:",playername,playernames[playername])
            self._players.append(Player(int(playername),playernames[playername], self._property_sets))

    def __str__(self):
        # text representation of board
        output = ""
        tile = 1
        for space in self._spaces:
            output += (str(tile) + ": " + str(space))
            tile += 1
        return output

    def _makeSpaces(self, filename):
        # parse a textfile to create appropiate space objects
        spaces = []
        decks = {}
        try:
            filehandle = open(filename, 'r')
            for line in filehandle:
                args = line.split(" * ")
                if args[0] == "PROPERTY":
                    spaces += [PropertySpace(args[1], int(args[2]), args[3])]
                    if args[3] not in self._property_sets:
                        # property sets mantains name of each set and the max number of properties in it
                        self._property_sets[args[3]] = [[], 1]
                    else:
                        self._property_sets[args[3]][1] += 1
                elif args[0] == "DECK":
                    if args[1] not in decks:
                        # only make each deck once and share across each space of same name
                        deck = self._makeDeck(args[2])
                        deckSpace = DeckSpace(args[1], deck)
                        decks[args[1]] = deckSpace
                        spaces += [deckSpace]
                    else:
                        spaces += [decks[args[1]]]
                elif args[0] == "TAX":
                    spaces += [TaxSpace(args[1], int(args[2]))]
                elif args[0] == "JAIL":
                    spaces += [Space(args[0], args[1])]
                    self._jail_pos = (len(spaces) - 1)
                elif args[0] in self._vaildtypes:
                    spaces += [Space(args[0], args[1])]
            return spaces
        except FileNotFoundError:
            print("Sorry couldn't find file '%s', please make sure it exists" % (filename))
            exit()

    def _makeDeck(self, filename):
        # makes a deck given a file of cards in the supported format
        deck = []
        try:
            filehandle = open(filename, 'r')
            for line in filehandle:
                args = line.split(" | ")
                if args[0] == "BAIL":
                    deck += [Card(args[0], args[1], True)]
                elif args[0] in self._vaildcardtypes:
                    deck += [Card(args[0], args[1], args[2])]
            # need to shuffle deck as it is read from file in same order each time
            random.shuffle(deck)
            return deck
        except FileNotFoundError:
            print("Sorry couldn't find file '%s', please make sure it exists" % (filename))
            exit()

    def getSize(self):
        # returns the number of valid positions on the board e.g 39 for the standard 40sq
        return len(self._spaces) - 1

    def getSpace(self, pos):
        # returns the space object at a specified position pos
        return self._spaces[pos]

    def getJailPosition(self):
        # tells you which space on the board corresponds to jail
        return self._jail_pos

    def getPlayer(self, player_id):
        # returns the player object with given id
        return self._players[player_id]

    def removePlayer(self,player_id):
        # take a player out of the game and handle all their missing properties
        player = self.getPlayer(player_id)
        player.takeMoney(player.getBalance())
        groups = player.getProperties()
        for group in groups:
            for space in groups[group][0]:
                player.removeProperty(space)

    def getPlayerList(self):
        # returns a copy of the list of players in game
        player_list = list(self._players)
        return player_list

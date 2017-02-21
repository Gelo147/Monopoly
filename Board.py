from Space import Space
from PropertySpace import PropertySpace
from DeckSpace import DeckSpace
from Card import Card
from Player import Player
class Board:
    """The representation of the game board where most of the action takes place"""
    def __init__(self,filename,playernames):
        self._vaildtypes = ["GO","PROPERTY","JAIL","FREE","GOTOJAIL"]
        self._vaildcardtypes = ["COLLECT","BAIL","PAY","GOTO"]
        self._property_sets = {}
        self._spaces = self._makeSpaces(filename)
        self._players = []
        for i in sorted(playernames):
            self._players.append(Player(i,playernames[i],self._property_sets))
    def __str__(self):
        #text representation of board
        output = ""
        tile =1
        for space in self._spaces:
            output += (str(tile) +": " + str(space))
            tile+=1
        return output
            
    
    def _makeSpaces(self,filename):
        spaces = []
        decks = {}
        try:
            filehandle = open(filename,'r')
            for line in filehandle:
                    args = line.split(" * ")
                    if args[0] == "PROPERTY":
                        spaces += [PropertySpace(args[1],int(args[2]),args[3])]
                        if args[3] not in self._property_sets:
                            self._property_sets[args[3]] = [[],1]
                        else:
                            self._property_sets[args[3]][1]+=1
                    elif args[0] == "DECK":
                        if args[1] not in decks:
                            deck = self._makeDeck(args[2])
                            deckSpace = DeckSpace(args[1],deck)
                            decks[args[1]] = deckSpace
                            spaces += [deckSpace]
                        else:
                            spaces += [decks[args[1]]]
                    elif args[0] in self._vaildtypes:
                        spaces += [Space(args[0],args[1])]
            return spaces
        except FileNotFoundError:
                print("Sorry couldn't find file '%s', please make sure it exists" % (filename))
                exit()

    def _makeDeck(self,filename):
        #makes a deck given a file of cards in the supported format
        deck = []
        try:
            filehandle = open(filename,'r')
            for line in filehandle:
                    args = line.split(" | ")
                    if args[0] == "BAIL":
                        deck += [Card(args[0],args[1],True)]
                    elif args[0] in self._vaildcardtypes:
                        deck += [Card(args[0],args[1],args[2])]
            return deck
        except FileNotFoundError:
                print("Sorry couldn't find file '%s', please make sure it exists" % (filename))
                exit()
                             
    def getSize(self):
        return len(self._spaces) -1
                             
    def getSpace(self,pos):
        return self._spaces[pos]
                             
    def getPlayer(self,player_id):
        return self._players[player_id]

    def getPlayerList(self):
        player_list = list(self._players)
        return player_list

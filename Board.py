from Space import Space
from PropertySpace import PropertySpace
from Player import Player
class Board:
    """The representation of the game board where most of the action takes place"""
    def __init__(self,filename,playernames):
        self.vaildtypes = ["GO","PROPERTY","JAIL","FREE","GOTOJAIL"]
        self.property_sets = {}
        self.spaces = self.makeSpaces(filename)
        self.players = []
        for i in sorted(playernames):
            self.players.append(Player(i,playernames[i],self.property_sets))
    def __str__(self):
        #text representation of board
        output = ""
        tile =1
        for space in self.spaces:
            output += (str(tile) +": " + str(space))
            tile+=1
        return output
            
    
    def makeSpaces(self,filename):
        spaces = []
        try:
            filehandle = open(filename,'r')
            for line in filehandle:
                    args = line.split(" * ")
                    if args[0] == "PROPERTY":
                            spaces += [PropertySpace(args[1],int(args[2]),args[3])]
                            if args[3] not in self.property_sets:
                                self.property_sets[args[3]] = [[],1]
                            else:
                                self.property_sets[args[3]][1]+=1
                    elif args[0] in self.vaildtypes:
                            spaces += [Space(args[0],args[1])]
            return spaces
        except FileNotFoundError:
                print("Sorry couldn't find file '%s', please make sure it exists" % (filename))
                exit()
                             
    def getSize(self):
        return len(self.spaces) -1
                             
    def getSpace(self,pos):
        return self.spaces[pos]
                             
    def getPlayer(self,player_id):
        return self.players[player_id]

    def getPlayerList(self):
        player_list = list(self.players)
        return player_list

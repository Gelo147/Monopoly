from Space import Space
from PropertySpace import PropertySpace
class Board:
    """The representation of the game board where most of the action takes place"""
    def __init__(self,filename,playernames):
        self.vaildtypes = ["GO","PROPERTY","JAIL","FREE","GOTOJAIL"]
        self.spaces = self.makeSpaces(filename)
        self.players = []
        for i in range(len(playernames):
            self.players += [Player(i+1,playernames[i])
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
                            spaces += [PropertySpace(args[1],args[2],args[3])]
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
        return self.players[player_id-1]

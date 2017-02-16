class Board:
    """The representation of the game board where most of the action takes place"""
    def __init__(self,filename):
		self.vaildtypes = ["GO","PROPERTY","JAIL","FREE","GOTOJAIL]"]
        self.spaces = self.makeSpaces(filename)
        
    def __str__(self):
        #text representation of board
        return "[Board looks like this]"
    
    def makeSpaces(self,filename):
        try:
            filehandle = open(filename,'r')
            for line in filehandle:
                    args = line.split("*")
                    if args[0] == "PROPERTY":
                            self.spaces += [PropertySpace(args[0],args[2],args[3])]
                    else if args[0] in self.vaildtypes:
                            self.spaces += [Space(args[0],args[1])]
        except FileNotFoundError:
                print("Sorry couldn't find file '%s', please make sure it exists" % (filename))
                                

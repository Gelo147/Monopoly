from Space import Space
class PropertySpace(Space):
    def __init__(self,text,rent,colour):
        super().__init__("PROPERTY",text)
        self.rent = rent
        self.colour = colour
        self.owner = None
        
    def __str__(self):
        owner = ""
        if self.owner:
            owner = " // Owned by: Player " + str(self.owner)
        return "[Group:%s // %s // %s%s]\n" % (self.colour,self.text,str(self.rent)+'€',owner)
    
    def getRent(self):
        return self.rent
    
    def getOwner(self):
        return self.owner
    
    def setOwner(self,player_id):
        self.owner = player_id
        print(self.owner)
        

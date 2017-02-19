from Space import Space
class PropertySpace(Space):
    def __init__(self,text,rent,group):
        super().__init__("PROPERTY",text)
        self.rent = rent
        self.group = group
        self.owner = None
        self.bonus = False
        
    def __str__(self):
        owner = ""
        if self.owner:
            owner = " // Owned by: Player " + str(self.owner)
        return "[Group:%s // %s // %s%s]\n" % (self.group,self.text,str(self.rent)+'€',owner)
    
    def getRent(self):
        return self.rent
    
    def getOwner(self):
        return self.owner
    
    def setOwner(self,player_id):
        self.owner = player_id
        
    def getGroup(self):
        return self.group
    
    def addBonus(self):
        self.rent*=2
        
    def removeBonus(self):
        self.rent = self.rent / 2
        
        

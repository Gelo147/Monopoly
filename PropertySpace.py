from Space import Space
class PropertySpace(Space):
    def __init__(self,text,price,group):
        super().__init__("PROPERTY",text)
        self._price = price
        self._rent = price/ 4
        self._group = group
        self._owner = None
        self._bonus = False
        
    def __str__(self):
        owner = ""
        cost = self._price
        if self._owner is not None:
            owner = " // Owned by: Player " + str(self._owner)
            cost = self._rent
        return "[Group:%s // %s // %s%s]\n" % (self._group,self._text,str(cost)+'€',owner)
    
    def getRent(self):
        return self._price / 4
    def getPrice(self):
        return self._price
    
    def getOwner(self):
        return self._owner
    
    def setOwner(self,player_id):
        self._owner = player_id
        
    def getGroup(self):
        return self._group
    
    def addBonus(self):
        self._rent*=2
        
    def removeBonus(self):
        self._rent = self._rent / 2
        
        

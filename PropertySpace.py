class PropertySpace(Space):
    def __init__(self,text,rent,colour):
        super.__init__(self,"PROPERTY",text)
        self.rent = rent
        self.colour = colour
        self.owner = None

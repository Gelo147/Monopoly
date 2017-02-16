def Space:
    """A space is a single spot on the board with unique text"""
    def __init__(self,text,space_type):
        self.text = text
        self.type = space_type

    def __str__(self):
        return self.text
    def getType(self):
        return self.type
        
        

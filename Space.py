class Space:
    """A space is a single spot on the board with unique text"""
    def __init__(self,space_type,text):
        self.text = text
        self.type = space_type

    def __str__(self):
        return "[%s]\n" % (self.text)
    def getType(self):
        return self.type
    def getText(self):
        return self.text

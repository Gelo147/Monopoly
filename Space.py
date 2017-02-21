class Space:
    """A space is a single spot on the board with unique text"""
    def __init__(self,space_type,text):
        self._text = text
        self._type = space_type

    def __str__(self):
        return "[%s]\n" % (self._text)
    def getType(self):
        return self._type
    def getText(self):
        return self._text

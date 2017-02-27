class StupidException(Exception):
    def __init__(self,message):
        super(StupidException,self).__init__(message)
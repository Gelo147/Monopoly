class Card:

    def __init__(self, text, is_bail, method):
        # Method must be a lambda that takes in a player object and the server
        self.__text = text
        self.__method = method
        self.__is_bail = is_bail

    def getText(self):
        return self.__text

    def isBail(self):
        return self.__is_bail

    def action(self, player, board):
        self.__method(player, board)

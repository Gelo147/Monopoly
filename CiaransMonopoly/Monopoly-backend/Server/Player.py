class Player:

    _CURRENT_ID = 0

    def __init__(self, name):
        self.setUsername(name)
        self.setBank()
        self.setGo()
        self.setInJail()
        self.setGetOutOfJailFreeCard()
        self.__id = Player._CURRENT_ID
        self.__jailCount = 0
        Player._CURRENT_ID += 1
        self.__ownedProperties = []

    def getId(self):
        return self.__id

    def setUsername(self, name):
        self.__name = name

    def getUsername(self):
        return self.__name

    def setBank(self):
        self.__bankBal = 1500

    def updateBank(self, value):
        self.__bankBal += value

    def getBankBal(self):
        return self.__bankBal

    def setGo(self):
        self.__pos = 0

    def movePosition(self, roll):
        """
        Updates the Player's current position
        :param roll: The dice roll the player made
        :return: True if the Player passed go else False
        """
        old_pos = self.__pos
        self.__pos += roll
        self.__pos %= 40
        return old_pos > self.__pos

    def getPos(self):
        return self.__pos

    def setInJail(self):
        self.__inJail = False

    def getInJail(self):
        return self.__inJail

    def updateJailCount(self):
        self.__jailCount += 1

    def resetJailCount(self):
        self.__jailCount = 0

    def getJailCount(self):
        return self.__jailCount

    def goToJail(self):
        self.__inJail = True

    def getOutOfJail(self):
        self.__inJail = False

    def setGetOutOfJailFreeCard(self):
        self.__jailCard = False

    def getJailCard(self):
        self.__jailCard = True

    def useJailCard(self):
        self.__jailCard = False
        self.__inJail = False

    def hasJailCard(self):
        return self.__jailCard

    def addOwnProp(self, prop):
        self.__ownedProperties.append(prop)

    def getOwnedProperties(self):
        return self.__ownedProperties

    def sellProp(self, prop):
        self.__ownedProperties.remove(prop)

    def __hash__(self):
        return self.__id

    def __eq__(self, obj):
        return isinstance(obj, Player) and self.__id == obj.getId()

    def __ne__(self, obj):
        return not self == obj

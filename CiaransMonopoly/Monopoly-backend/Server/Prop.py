class Prop:

    def __init__(self, name, price):
        self.__name = name
        self.__price = price
        self.__owner = None

    def getName(self):
        return self.__name

    def getPrice(self):
        return self.__price

    def getRent(self):
        rent = self.__price * .12
        # Ensure int TODO - Add rent to constructor
        return rent // 1

    def getOwner(self):
        return self.__owner

    def setOwner(self, owner):
        self.__owner = owner

    def setUnOwned(self):
        self.__owner = None

    def isOwned(self):
        return self.__owner is not None

    def __repr__(self):
        return self.__name

    def __eq__(self, obj):
        return isinstance(obj, Prop) and self.__name == obj.getName()

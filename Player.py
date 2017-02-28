##import json
import random
import copy


class Player:
    """ Class Player describes each player including how much money
and property they currently own"""

    def __init__(self, player_id, name, property_sets):
        # takes in an id, a name, and a dictionary describing the property groups
        self._id = player_id
        self._name = name
        self._position = 0
        self._balance = 1500
        self._properties = copy.deepcopy(property_sets)
        self._bankrupt = False
        self._jailed = False
        self._on_bail = False

    def __str__(self):
        # describes the player in plain text
        return self._name

    def addMoney(self, money):
        # add cash directy to current players balance
        self._balance += money

    def takeMoney(self, money):
        # take cash away from current players balance and update bankruptcy status
        self._balance -= money
        if self._balance <= 0:
            self._bankrupt = True

    def getName(self):
        # get the players name
        return self._name

    def getId(self):
        # get the id of the current player
        return self._id

    def getBalance(self):
        # get the balance of the current player (cash on hand)
        return self._balance

    def getPosition(self):
        # get the current position of the player on board
        return self._position

    def setPosition(self, position):
        # move the player to a specified position
        self._position = position

    def getProperties(self):
        # retuns a dictionary where key = name of property group, value = a list where first element is a list of property spaces
        # and second element is the max number of properties in that group
        return self._properties

    def addProperty(self, space):
        # sets owner on space and adds it to players collection of properties
        space.setOwner(self.getId())
        property_pair = self._properties[space.getGroup()]
        property_pair[0] += [space]
        if len(property_pair[0]) == property_pair[1]:
            # player owns all properties in group so activate set bonus
            print(self._name + " just got the set bonus for " + space.getGroup())
            for property_space in property_pair[0]:
                property_space.addBonus()

    def removeProperty(self, space):
        # resets owner on space and removes it from players collection of properties
        space.setOwner(None)
        property_pair = self._properties[space.getGroup()]
        property_pair[0].remove(space)
        if len(property_pair[0]) == property_pair[1] - 1:
            # player lost set bonus so deactivate it
            print(self._name + " just lost the set bonus for " + space.getGroup())
            for property_space in property_pair[0]:
                property_space.removeBonus()

    def isJailed(self):
        # check players jail status
        return self._jailed

    def updateJailed(self):
        # Changes player to go in or out of jail
        self._jailed = not self._jailed

    def hasBail(self):
        # check players jail status
        return self._on_bail

    def updateBail(self, bail_status):
        # Takes in a boolean which states if player is jailed or not
        self._on_bail = bail_status

    def isBankrupt(self):
        # check if the current player is bankrupt
        return self._bankrupt

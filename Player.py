##import json
import random
import copy
class Player:
    """ Class Player describes each player including how much money
and property they currently own"""
    def __init__(self,player_id,name,property_sets):
        #takes in an id and a name
        self.id = player_id
        self.name = name
        self.position = 0
        self.balance = 1500
        self.properties = copy.deepcopy(property_sets)
        self.bankrupt = False
        self.jailed = False
    def __str__(self):
        #describes the player in plain text
        return self.name

    def addMoney(self,money):
        #add cash directy to current players balance
        self.balance+=money
        
    def takeMoney(self,money):
        #take cash away from current players balance and update bankruptcy status
        self.balance-=money
        if self.balance <= 0:
            self.bankrupt = True
        
    def getName(self):
        #get the players name
        return self.name
    
    def getId(self):
        #get the id of the current player
        return self.id
    
    def getBalance(self):
        #get the balance of the current player (cash on hand)
        return self.balance
    
    def getPosition(self):
        #get the current position of the player on board
        return self.position
    
    def setPosition(self,position):
        #move the player to a specified position
        self.position = position

    def getProperties(self):
        return self.properties
    
    def addProperty(self,space):
        property_pair = self.properties[space.getGroup()]
        property_pair[0]+=[space]
        if len(property_pair[0]) == property_pair[1]:
            #player owns all properties in group so activate set bonus
            print(self.name + " just got the set bonus for " + space.getGroup())
            for property_space in property_pair[0]:
                property_space.addBonus()
        
    def removeProperty(self,space):
        space.setOwner(None)
        property_pair = self.properties[space.getGroup()]
        property_pair[0].remove(space)
        if len(property_pair[0]) == property_pair[1]-1:
            print("num is:",property_pair[1])
            #player lost set bonus so deactivate it
            print(self.name + " just lost the set bonus for " + space.getGroup())
            for property_space in property_pair[0]:
                print(property_space)
                property_space.removeBonus()
        
    def isJailed(self):
        return self.jailed
    
    def updateJailed(self,jail_status):
        self.jailed = jail_status
        
    def isBankrupt(self):
        #check if the current player is bankrupt
        return self.bankrupt
        

##import json
import random
class Player:
    """ Class Player describes each player including how much money
and property they currently own"""
    def __init__(self,player_id,name):
        #takes in an id and a name
        self.id = player_id
        self.name = name
        self.position = 0
        self.bankrupt = False
        self.balance = 1500
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
    
    def isBankrupt(self):
        #check if the current player is bankrupt
        return self.bankrupt
    
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
        
    def isJailed(self):
        return self.jailed
    
    def updateJailed(self,jail_status):
        self.jailed = jail_status

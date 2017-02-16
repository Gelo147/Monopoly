import json

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
        return "Player has blah blah"

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
    
    def setPosition:(self,position):
        #move the player to a specified position
        self.position = position
        
    def rollDice():
        request = {"command": "ROLL","values": {}}
        request_json = json.dumps(request)
        #send this data to server and await reply
        return [die1,die2]
    
    def resolveSpace(space):
        if space.getType() == 'property':
            #do property stuff here
             
    def takeTurn(self):
        #ask server to roll dice, make move and resolve space landed on
        doubles = 0
        turns = 1
        while turns > 0:
            roll = self.rollDice()
            if roll[0] == roll[1]:
                turns +=1
                doubles += 1
                if doubles == 3:
                    #3 doubles means go to jail
                    self.jailed = True
                    self.position = 9
                    return
            self.position += sum(roll)
            if self.position > board.getSize():
                #player passed go so add salary and wrap around to start of board
                self.position -= board.getSize()
                self.addMoney(200)
            self.resolveSpace(board.getSpace(self.position))
            turns -=1

        
        
        
    

    
        

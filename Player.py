##import json
import random
class Player:
    """ Class Player describes each player including how much money
and property they currently own"""
    def __init__(self,player_id,name,board):
        #takes in an id and a name
        self.id = player_id
        self.name = name
        self.board = board
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
        
    def rollDice(self):
        
        ##request = {"command": "ROLL","values": {}}
        ##request_json = json.dumps(request)
        #send this data to server and await reply
        die1 = random.randint(1,6)
        die2 = random.randint(1,6)
        print(self.name + " rolled a "+ str(die1) + " and a " + str(die2) + "!")
        return [die1,die2]
    
    def resolveSpace(self,space):
        if space.getType() == 'PROPERTY':
            price = int(space.getRent())
            if space.getOwner() and space.getOwner() != self.id:
                self.takeMoney(price)
                print(self.name + " just paid rent on '"+ space.getText() +"' costing them " + str(price) )
            elif self.balance > price:
                print(self.name + " just bought '"+ space.getText() +"' for " + str(price) )
                self.takeMoney(price)
                space.setOwner(self.id)
            
             
    def takeTurn(self):
        #ask server to roll dice, make move and resolve space landed on
        doubles = 0
        turns = 1
        while turns > 0:
            roll = self.rollDice()
            if roll[0] == roll[1]:
                if not self.jailed:
                    turns +=1
                doubles += 1
                if doubles == 3:
                    #3 doubles means go to jail
                    print(self.name + " is going to jail!")
                    self.jailed = True
                    self.position = 8
                    return
            elif self.jailed:
                #in jail and didn't roll double so pay bail
                print(self.name + " paid 50 to get outta jail!")
                self.takeMoney(50)
                self.jailed = False
            self.position += sum(roll)
            if self.position > self.board.getSize():
                #player passed go so add salary and wrap around to start of board
                self.position -= self.board.getSize()
                print(self.name + " passed go and got 200!")
                self.addMoney(200)
            self.resolveSpace(self.board.getSpace(self.position))
            turns -=1

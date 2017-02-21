from Board import Board
from Player import Player
import random

GO_CASH = 50
JAIL_FINE = 200

def game(board_file,num_players):
    #setup
    playernames = {}
    for i in range(num_players):
        playernames[i]=("Player "+str(i))
    board = Board(board_file,playernames)
    players = board.getPlayerList()
    #on_bail = {}

    
    
    
    #game loop
    current_round = 1
    while len(players)>1:
        print("Round: %i\n%s" % (current_round, board))
        for player in players:
            print("%s has %i€ and is on space %i." %(player.getName(),player.getBalance(),player.getPosition()+1))
            if player.isBankrupt():
                print("%s has gone bankrupt and is out of the game. %i player(s) remain." %(player.getName(),len(players)-1))
                removePlayer(player)
                players.remove(player)
                if len(players) == 1:
                    break
            else:
                takeTurn(player,board)
        current_round+=1
    print(players[0].getName() + " is the winner! Thanks for playing!")
    
def test():
    game("Ireland6x4Monopoly.txt",4)

def rollDice(player):
    die1 = random.randint(1,6)
    die2 = random.randint(1,6)
    print(player.getName() + " rolled a "+ str(die1) + " and a " + str(die2) + "!")
    return [die1,die2]

def resolveSpace(player,board):
        space = board.getSpace(player.getPosition())
        space_type = space.getType()
        if  space_type == "PROPERTY":
            #if it's a property we check who owns it and resolve appropiately
            price = int(space.getRent())
            owner_id = space.getOwner()
            if owner_id is not None and owner_id != player.getId():
                #someone else owns the space so player pays them
                player.takeMoney(price)
                owner = board.getPlayer(owner_id)
                owner.addMoney(price)
                print(player.getName() + " just paid rent on '"+ space.getText() +"' giving " + owner.getName() + " the amount of " + str(price)) 
            elif owner_id is None and player.getBalance() > price:
                #no one owns the space so player auto buys it if funds allow
                print(player.getName() + " just bought '"+ space.getText() +"' for " + str(price) )
                player.takeMoney(price)
                player.addProperty(space)
        elif space_type == "TAX":
            #if it's a tax space player pays the fee
            player.takeMoney(space.getFee())
            print(player.getName() + " just paid a tax of " + str(space.getFee())) 
        elif space_type  == "DECK":
            #if it's a card space draw a card and handle it
            card = space.drawCard()
            handleCard(player,card)
        elif space_type  == "GOTOJAIL":
            #if the space is go to jail send the player to jail and tell them they are jailed
            print(player.getName() + " is going to jail!")
            player.updateJailed(True)
            player.setPosition(8)

def handleCard(player,card):
    #takes a card and a player and sends the card to the player then performs appopiate action
    print(player.getName() + " drew this card: ['" + card.getText() +"']")
    card_type = card.getType()
    card_value = card.getValue()

    if card_type == 'COLLECT':
        #send CARD then PAY from None to player
        player.addMoney(int(card_value))
        print(player.getName() + " just collected an amount of " + str(card_value))
    elif card_type == 'PAY':
        #send CARD then PAY from player to None
        player.takeMoney(int(card_value))
        print(player.getName() + " just paid an amount of " + str(card_value)) 
    elif card_type == 'BAIL':
        #send CARD with bail type True
        print(player.getName() + " is now on bail")
        #on_bail.add(player)
    elif card_type == 'GOTO':
        #send CARD then GOTO with players new position
        if card_value == 'JAIL':
            print(player.getName() + " is going to jail!")
            player.updateJailed(True)
            player.setPosition(8)
        elif card_value == 'GO':
            print(player.getName() + " set to go and got " + str(GO_CASH))
            player.addMoney(GO_CASH)
            player.setPosition(0)
        else:
            player.setPosition(int(card_value))


    
    
def takeTurn(player,board):
        #ask server to roll dice, make move and resolve space landed on
        doubles = 0
        turns = 1
        while turns > 0:
            roll = rollDice(player)
            if roll[0] == roll[1]:
                if not player.isJailed():
                    turns +=1
                doubles += 1
                if doubles == 3:
                    #3 doubles means go to jail
                    print(player.getName() + " rolled 3 doubles and is going to jail!")
                    player.updateJailed(True)
                    player.setPosition(8)
                    return
            elif player.isJailed():
                #in jail and didn't roll double so pay bail
                print(player.getName() + " paid",JAIL_FINE,"to get outta jail!")
                player.takeMoney(JAIL_FINE)
                player.updateJailed(False)
                
            player.setPosition(player.getPosition()+sum(roll))
            if player.getPosition()> board.getSize():
                #player passed go so add salary and wrap around to start of board
                player.setPosition(player.getPosition()- board.getSize())
                print(player.getName()+ " passed go and got "+str(GO_CASH)+"!")
                player.addMoney(GO_CASH)
            resolveSpace(player,board)
            turns -=1    

def removePlayer(player):
    #take a player out of the game and handle all their missing properties
    groups = player.getProperties()
    for group in groups:
        for space in groups[group][0]:
            player.removeProperty(space)
            

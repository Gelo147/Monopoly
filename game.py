from Board import Board
from Player import Player
import random

def game(board_file,num_players):
    #setup
    playernames = {}
    for i in range(num_players):
        playernames[i]=("Player "+str(i))
    board = Board(board_file,playernames)
    players = board.getPlayerList()
    print(players)
    
    
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
    game("Ireland4x4Monopoly.txt",4)

def rollDice(player):
    die1 = random.randint(1,6)
    die2 = random.randint(1,6)
    print(player.getName() + " rolled a "+ str(die1) + " and a " + str(die2) + "!")
    return [die1,die2]

def resolveSpace(player,board):
        space = board.getSpace(player.getPosition())
        if space.getType() == 'PROPERTY':
            #if it's a property we check who owns it and resolve appropiately
            price = int(space.getRent())
            owner_id = space.getOwner()
            if owner_id and owner_id != player.getId():
                #someone else owns the space so player pays them
                player.takeMoney(price)
                owner = board.getPlayer(owner_id)
                owner.addMoney(price)
                print(player.getName() + " just paid rent on '"+ space.getText() +"' giving " + owner.getName() + " the amount of " + str(price)) 
            elif player.getBalance() > price:
                #no one owns the space so player auto buys it if funds allow
                print(player.getName() + " just bought '"+ space.getText() +"' for " + str(price) )
                player.takeMoney(price)
                space.setOwner(player.getId())
                player.addProperty(space)
    
    
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
                    print(player.getName() + " is going to jail!")
                    player.updateJailed(True)
                    player.setPosition(8)
                    return
            elif player.isJailed():
                #in jail and didn't roll double so pay bail
                print(player.getName() + " paid 50 to get outta jail!")
                player.takeMoney(50)
                player.updateJailed(False)
                
            player.setPosition(player.getPosition()+sum(roll))
            if player.getPosition()> board.getSize():
                #player passed go so add salary and wrap around to start of board
                player.setPosition(player.getPosition()- board.getSize())
                print(player.getName()+ " passed go and got 200!")
                player.addMoney(200)
            resolveSpace(player,board)
            turns -=1    

def removePlayer(player):
    #take a player out of the game and handle all their missing properties
    groups = player.getProperties()
    for group in groups:
        for space in groups[group][0]:
            player.removeProperty(space)
    
                
    

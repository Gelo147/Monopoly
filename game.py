from Board import Board
from Player import Player
def game(board_file,num_players):
    #setup
    board = Board(board_file)
    players = []
    for i in range(1,num_players+1):
        players += [Player(i,"Player "+str(i),board)]
    
    #game loop
    current_round = 1
    while len(players)>1:
        print("Round: %i\n%s" % (current_round, board))
        for player in players:
            print("%s has %i€ and is on space %i." %(player.getName(),player.getBalance(),player.getPosition()+1))
            if player.isBankrupt():
                print("%s has gone bankrupt and is out of the game. %i player(s) remain." %(player.getName(),len(players)-1))
                players.remove(player)
                if len(players) == 1:
                    break
            else:
                player.takeTurn()
        current_round+=1
    print(str(players[0]) + " is the winner! Thanks for playing!")
def test():
    game("Ireland4x4Monopoly.txt",4)
    
                
    

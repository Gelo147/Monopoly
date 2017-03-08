from collections import deque
from random import randint, shuffle

from .Card import Card
from .OtherTile import OtherTile
from .Prop import Prop


class Board:
    def __init__(self, server):
        self.server = server
        self.__players = []
        self.__current_turn = 0
        self.__current_doubles = 0
        self.__winner = None
        self.__freeParking = 0
        self.__properties = []
        self.__chance = None
        self.__comm_chest = None
        self.curr_round = 0
        self.initialise_board()
        self.initialise_cards()

    def initialise_board(self):
        self.__properties = [
            OtherTile("GO"),                               # 00
            Prop("Cork City Gaol Heritage Centre", 60),    # 01
            OtherTile("Community Chest"),                  # 02
            Prop("Mizen Head", 60),                        # 03
            OtherTile("Income Tax"),                       # 04
            Prop("Kent Station", 200),                     # 05
            Prop("Cork Opera House", 100),                 # 06
            OtherTile("Chance"),                           # 07
            Prop("Trabolgan Holiday Vilage", 100),         # 08
            Prop("The English Market", 120),               # 09
            OtherTile("Jail (Just Visiting)"),             # 10
            Prop("Cork Racecourse Mallow", 140),           # 11
            Prop("Electric Company", 150),                 # 12
            Prop("Kinsale Golf Course", 140),              # 13
            Prop("Munster Rugby", 160),                    # 14
            Prop("Parnell Place Bus Station", 200),        # 15
            Prop("St Patrick Street", 180),                # 16
            OtherTile("Community Chest"),                  # 17
            Prop("Opera Lane", 180),                       # 18
            Prop("Merchants Quay Shopping Centre", 200),   # 19
            OtherTile("Free Parking"),                     # 20
            Prop("Blackrock Castle", 220),                 # 21
            OtherTile("Chance"),                           # 22
            Prop("Irish Examiner", 220),                   # 23
            Prop("Fota Wildlife Park", 240),               # 24
            Prop("Cork Airport", 200),                     # 25
            Prop("Cork Butter Museum", 260),               # 26
            Prop("City Hall", 260),                        # 27
            Prop("The Lifetime Lab", 150),                 # 28
            Prop("University College Cork", 280),          # 29
            OtherTile("Go To Jail"),                       # 30
            Prop("Jameson Visitor Centre", 300),           # 31
            Prop("Fota House", 300),                       # 32
            OtherTile("Community Chest"),                  # 33
            Prop("Cobh Heritage Centre", 320),             # 34
            Prop("Port of Cork", 200),                     # 35
            OtherTile("Chance"),                           # 36
            Prop("Shandon Bells", 350),                    # 37
            OtherTile("Bank Deposit"),                     # 38
            Prop("Blarney Castle", 400)                    # 39
        ]

    def initialise_cards(self):
        # Chance cards
        chance = [
            Card("Advance to Go. Collect €200", False,
                 lambda player, board: board.player_move(player, 40 - player.getPos())),
            Card("Go to Fota Wildlife Park", False,
                 lambda player, board: board.player_move(player, 64 - player.getPos())),
            Card("Go to Cork Racecourse Mallow", False,
                 lambda player, board: board.player_move(player, 51 - player.getPos())),
            Card("Go to The Lifetime Lab", False,
                 lambda player, board: board.player_move(player, 68 - player.getPos())),
            Card("Go to Kent Station", False,
                 lambda player, board: board.player_move(player, 45 - player.getPos())),
            Card("The bank finally has your money. Collect €50", False,
                 lambda player, board: (player.updateBank(50), board.server.send_pay(50, None, player))),
            Card("Get out of jail free card. This card may be kept until needed", True,
                 lambda player, board: None),
            Card("Go back 3 spaces", False,
                 lambda player, board: board.player_move(player, -3)),
            Card("Go to Jail. Go directly to Jail. Do not pass Go. Do not collect €200", False,
                 lambda player, board: board.send_to_jail(player)),
            Card("You were a mess and got sick in the taxi. Pay €30", False,
                 lambda player, board: (player.updateBank(-15), board.server.send_pay(15, player, None))),
            Card("Take a kayak. Go to the Port of Cork", False,
                 lambda player, board: board.player_move(player, 75 - player.getPos())),
            Card("Kiss the Blarney Stone", False,
                 lambda player, board: board.player_move(player, 79 - player.getPos())),
            Card("Repay everyone's water tax. Pay each player €50", False,
                 lambda player, board: [(player.updateBank(-50), other.updateBank(50),
                                         board.server.send_pay(50, player, other))
                                        for other in board.__players if other != player]
                 ),
            Card("You have won a GAA Lottery. Collect €100", False,
                 lambda player, board: (player.updateBank(100), board.server.send_pay(100, None, player))),
            Card("You were caught drinking in public. Pay €75", False,
                 lambda player, board: (player.updateBank(-75), board.server.send_pay(75, player, None))),
            Card("You collect the dole. Collect €50", False,
                 lambda player, board: (player.updateBank(50), board.server.send_pay(50, None, player))),
            Card("Netflix subscription due. Pay €10", False,
                 lambda player, board: (player.updateBank(-10), board.server.send_pay(10, player, None))),
            Card("Your free texts expired. Pay €20", False,
                 lambda player, board: (player.updateBank(-20), board.server.send_pay(20, player, None))),
        ]
        shuffle(chance)
        self.__chance = deque(chance)
        community_chest = [
            Card("Advance to Go. Collect €200", False,
                 lambda player, board: board.player_move(player, 40 - player.getPos())),
            Card("Bank error in your favor. Collect €200", False,
                 lambda player, board: (player.updateBank(200), board.server.send_pay(200, player, None))),
            Card("Southdoc Fee. Pay €80", False,
                 lambda player, board: (player.updateBank(-80), board.server.send_pay(80, player, None))),
            Card("Sold your iPhone 4 on DoneDeal. Collect €50", False,
                 lambda player, board: (player.updateBank(50), board.server.send_pay(50, player, None))),
            Card("You ran an underground rave. Collect €50 from every player.", False,
                 lambda player, board: [(player.updateBank(50), other.updateBank(-50),
                                         board.server.send_pay(50, player, other))
                                        for other in board.__players if other != player]
                 ),
            Card("Christmas Dole Bonus. Collect €100", False,
                 lambda player, board: (player.updateBank(100), board.server.send_pay(100, None, player))),
            Card("Get out of jail free card. This card may be kept until needed", True,
                 lambda player, board: None),
            Card("You got tax back boi. Collect €20", False,
                 lambda player, board: (player.updateBank(20), board.server.send_pay(20, None, player))),
            Card("Go to Jail. Go directly to Jail. Do not pass Go. Do not collect €200", False,
                 lambda player, board: board.send_to_jail(player)),
            Card("It's your birthday, collect €10 from each player", False,
                 lambda player, board: [(player.updateBank(10), other.updateBank(-10),
                                         board.server.send_pay(10, other, player))
                                        for other in board.__players if other != player]
                 ),
            Card("Life insurance matures. Collect €100", False,
                 lambda player, board: (player.updateBank(100), board.server.send_pay(100, None, player))),
            Card("You hit your head on a night out. You need 10 stitches. Pay hospital €100", False,
                 lambda player, board: (player.updateBank(-100), board.server.send_pay(100, player, None))),
            Card("You broke a window at the Science Ball. Pay the hotel €150", False,
                 lambda player, board: (player.updateBank(-150), board.server.send_pay(150, player, None))),
            Card("You sold a 25 bag. Collect €25", False,
                 lambda player, board: (player.updateBank(25), board.server.send_pay(25, None, player))),
            Card("Your horse came second. Collect €20 from the bookies", False,
                 lambda player, board: (player.updateBank(20), board.server.send_pay(20, None, player))),
            Card("You visit your grandparents. Collect €100", False,
                 lambda player, board: (player.updateBank(100), board.server.send_pay(100, None, player))),
            Card("Enda needs more funds for his event center. Pay €100", False,
                 lambda player, board: (player.updateBank(-100), board.server.send_pay(100, player, None))),
            Card("You won the 96FM CashCall. Collect €100.", False,
                 lambda player, board: (player.updateBank(100), board.server.send_pay(100, None, player)))
        ]
        shuffle(community_chest)
        self.__comm_chest = deque(community_chest)

    def add_player(self, player):
        self.__players.append(player)

    def start(self):
        self.begin_turn()

    def handle_roll(self, player):
        dice1 = randint(1, 6)
        dice2 = randint(1, 6)
        self.server.send_event("%s rolled (%i, %i)" % (player.getUsername(), dice1, dice2))
        result = dice1 + dice2
        # Determine the situation for doubles
        if dice1 == dice2:
            # Are they already in jail?
            if player.getInJail():
                # They've been let out
                player.setInJail()
                self.server.send_jailed(player)
            else:
                # They just rolled another double
                self.__current_doubles += 1
        # Elif they are in jail already and they didn't roll a double
        elif player.getInJail():
            player.updateJailCount()
            if player.getJailCount() >= 3:
                # Unjail them and make them pay 50
                self.server.send_jailed(player)
                self.server.send_pay(50, player, None)
                self.server.send_event("%s paid bail of 50!" % (player.getUsername()))
                player.resetJailCount()
                player.getOutOfJail()

        # Now check if the player needs to be sent to jail
        if self.__current_doubles >= 3:
            self.server.send_event("%s was sent to Jail for rolling 3 doubles" % (player.getUsername()))
            self.send_to_jail(player)
        else:
            self.server.send_roll(player, [dice1, dice2])
            if not player.getInJail():
                self.player_move(player, result)
                # If the player is not in jail we can send a goto also
                self.server.send_goto(player, player.getPos())

    def handle_end(self, player):
        self.__current_doubles = 0
        if player.getBankBal() < 0:
            self.__players.remove(player)
            self.server.send_event("Player \"%s\" is bankrupt and was removed from the game" % player.getUsername())
            owns = [self.__properties.index(prop) for prop in player.getOwnedProperties()]
            self.server.send_sold(player, owns)
            for prop_id in owns:
                self.__properties[prop_id].setUnOwned()

        if len(self.__players) == 1:
            winner = self.__players[0]
            self.server.send_event("Player \"%s\" won the game with %i in their bank account, game over!" % (
                winner.getUsername(), winner.getBankBal()))
            self.server.end_game()
        self.__current_turn = (self.__current_turn + 1) % len(self.__players)
        self.begin_turn()

    def begin_turn(self):
        if self.__current_turn == 0:
            # TODO - Remove later
            self.curr_round += 1
            self.server.send_event("Round %i - %s" % (self.curr_round, str({p.getUsername(): p.getBankBal() for p in self.__players})))
        self.server.send_turn(self.__players[self.__current_turn])

    def player_move(self, player, dice_result):
        # Update player position
        if player.movePosition(dice_result):
            # Player has passed go
            player.updateBank(200)
            self.server.send_pay(200, None, player)
            self.server.send_event("%s passed GO!" % player.getUsername())

        pos = player.getPos()
        tile = self.__properties[player.getPos()]
        self.server.send_event("%s moved to %s" % (player.getUsername(), tile.getName()))

        # Player landed on send to jail
        if pos == 30:
            self.send_to_jail(player)

        # Player landed on a chance / community chest
        elif pos in [2, 17, 33]:
            card = self.__comm_chest.popleft()
            self.server.send_event("%s drew a Community Chest card: %s" % (player.getUsername(), card.getText()))
            card.action(player, self)
            self.__comm_chest.append(card)
            if card.isBail():
                player.getJailCard()
        elif pos in [7, 22, 36]:
            card = self.__comm_chest.popleft()
            self.server.send_event("%s drew a Chance card: %s" % (player.getUsername(), card.getText()))
            card.action(player, self)
            self.__comm_chest.append(card)
            if card.isBail():
                player.getJailCard()

        # Player landed on tax
        elif pos == 4:
            player.updateBank(-200)
            self.server.send_pay(200, player, None)
            self.__freeParking += 200

        elif pos == 38:
            player.updateBank(-100)
            self.server.send_pay(100, player, None)
            self.__freeParking += 100

        # Player landed on free parking
        elif pos == 20:
            player.updateBank(self.__freeParking)
            self.server.send_pay(self.__freeParking, None, player)
            self.__freeParking = 0

        # Check other special tiles
        elif pos in [0, 10]:
            pass

        # No special tile, normal property
        else:
            prop = self.__properties[pos]
            if prop.isOwned():
                owner = prop.getOwner()
                if owner != player and not owner.getInJail():
                    rent = prop.getRent()
                    owner.updateBank(rent)
                    player.updateBank(rent * -1)
                    self.server.send_pay(rent, player, owner)
                    self.server.send_event("%s payed %i in rent to %s for %s" % (
                        player.getUsername(),
                        rent,
                        owner.getUsername(),
                        prop.getName()
                    ))
            else:
                self.server.send_buy_request(player)

    def send_to_jail(self, player):
        player.goToJail()
        player.movePosition(10)
        self.server.send_goto(player, 10)
        self.server.send_event("%s was sent to Jail!" % (player.getUsername()))
        if player.hasJailCard():
            self.server.send_event("%s used a Bail Card!" % (player.getUsername()))
            player.useJailCard()
        else:
            self.server.send_jailed(player)

    def handle_buy(self, player):
        pos = player.getPos() % 40
        prop = self.__properties[pos]
        prop.setOwner(player)
        player.addOwnProp(prop)
        amount = prop.getPrice()
        self.server.send_pay(amount, player, None)
        player.updateBank(amount * -1)
        self.server.send_event("%s bought %s for %i" % (player.getUsername(), prop.getName(), amount))

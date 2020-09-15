class Game():
    def __init__(self, uuid, title, numPlayers, creator, status):
        self.gameID = uuid
        self.title = title
        self.creator = creator
        self.numPlayers = numPlayers
        self.status = status

        self.players = []  # List of all players in a game

        self.rules = {}  # store all game rules
        self.triggers = {}  # store all triggers for each action
        self.replacements = {}  # store all replacment effects

        self.zones = {Zone.STACK: [], Zone.FIELD: set()}
        self.allCards = {}
        self.GAT = {}  # Global Ability Table
        self.GMT = {}  # Global Modifier Table
        self.COMBAT_MATRIX = {}
        self.costModifiers = []
        self.trackers = []

        self.activePlayer = None
        self.currPhase = None
        self.priority = None
        self.waitingOn = None
        self.passedInSuccession = False

        self.won = False
        self.winners = []

    def getCard(self, instanceID):
        if instanceID in self.allCards:
            return self.allCards[instanceID]

    def AddZone(self, zoneController, zoneType, zoneObject):
        if zoneController not in self.zones:
            self.zones[zoneController] = {}
        self.zones[zoneController][zoneType] = zoneObject

    def getZone(self, zoneController, zoneType):
        return self.zones[zoneController][zoneType]

    def applyModifiers(self, card):
        pass

    def findCardByMemID(self, memID, zoneController, zoneType):
        zone = self.getZone(zoneController, zoneType)
        for card in zone:
            if card.getMemID() == memID:
                return card
        return None

    def resolve(self, obj):
        if isinstance(obj, Card) and obj.isPermanent:
            gameActions.evaluate(
                self, gameActions.moveToZone, obj, Zone.FIELD, None)
        else:
            for effect in obj.effect:
                gameActions.evaluate(self, **effect)

    def push(self, obj):
        pass

    def pop(self):
        self.resolve(self.zones[Zone.STACK][0])
        self.replacedBy = []
        pass

    def findPlayer(self, playerID):
        for player in self.players:
            if player.playerID == playerID:
                return player

    def getNextPlayer(self, player):
        return

    def getRelativePlayerList(self, activePlayer):

        lst = []
        started = False

        for player in self.players:
            if started:
                lst.append(player)
            elif player == activePlayer:
                lst.append(player)
                started = True

        for player in self.players:
            if player != activePlayer:
                lst.append(player)
            else:
                break

        return lst

    def getOpponents(self, chosenPlayer):
        return self.getRelativePlayerList(chosenPlayer)[1:]

    def addKeywordAbility(self, keyword):
        # Complete in __init__ for ability
        pass

    def addPlayerToGame(self, player):
        self.players.append(player)

    def removePlayerFromGame(self, player):
        self.players.remove(player)

    async def prep(self, rules):
        # loop used to setup the player's decks and other setup components
        for player in self.players:  # import cards into player's decks
            for key in player.cards:
                result = cards_db.find_one(name=key)
                module_ = import_module(result['filepath'])
                class_ = getattr(module_, result['name'].replace(" ", "").replace("'", ""))
                for _ in range(player.cards[key]):
                    card = class_(self, player, key)
                    player.deck.append(card)
                    card.currentZone = Zone.DECK

            shuffle(player.deck)  # shuffle player's decks

            msg3 = {
                "gameID": self.gameID,
                "playerID": player.playerID,
                "zoneType": "Zone.DECK",
                "num": len(player.deck)
            }

            self.notifyAll("Zone Size Update", msg3)

            self.notifyAll("Life Total Update", {
                "gameID": self.gameID,
                "playerID": player.playerID,
                "life": player.lifeTotal
            })

            # each player draws seven cards
            gameActions.drawCards(self, player, 7)

        # let the current task sleep so that the messages emitted during setup can go through
        await asyncio.sleep(0)

    async def run(self):
        self.currPhase = Turn.UNTAP
        self.activePlayer = self.players[0]

        # Use try except to check for win

        while not self.won:  # main gameplay loop
            await basicFunctions.doPhaseActions(self)
            self.passedInSuccession = False
            while not self.passedInSuccession and (self.currPhase != Turn.UNTAP or (self.currPhase == Turn.CLEANUP and self.zones[Zone.STACK] != [])):
                self.passedInSuccession = True
                for player in self.getRelativePlayerList(self.activePlayer):
                    # checkSBA(self)
                    basicFunctions.givePriority(self, player)
                    await basicFunctions.doAction(self, player)

            if self.zones[Zone.STACK] != []:
                self.pop()
            else:
                gameActions.evaluate(self, basicFunctions.goToNextPhase)

    def notifyAll(self, event, msg):
        asyncio.create_task(sio.emit(event, msg, room=self.gameID))

    def notify(self, event, msg, player):
        asyncio.create_task(sio.emit(event, msg, player.sid))

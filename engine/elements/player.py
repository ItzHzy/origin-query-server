class Player():
    def __init__(self, game, name, sid):
        self.game = game
        self.name = name
        self.playerID = "P-" + str(uuid1())
        self.pfp = None
        self.flavorText = "Someday, someone will best me. But it won't be today, and it won't be you."

        self.lifeTotal = 20
        self.deck = []
        self.hand = set()
        self.maxHand = 7
        self.grave = set()
        self.exile = set()
        self.abilities = set()
        self.counters = {}
        self.property = {}
        self.manaPool = {Color.WHITE: 0, Color.BLUE: 0, Color.BLACK: 0,
                         Color.RED: 0, Color.GREEN: 0, Color.COLORLESS: 0}

        self.passed = False
        self.awaitingTriggers = []

        self.hasSplice = False

        self.isHost = False
        self.sid = sid
        self.cards = None
        self.isReady = False
        self.answer = None
        self.chosenAction = None

        self.isDefending = False

        self.game.AddZone(self, Zone.DECK, self.getDeck())
        self.game.AddZone(self, Zone.GRAVE, self.getGrave())
        self.game.AddZone(self, Zone.EXILE, self.getExile())
        self.game.AddZone(self, Zone.HAND, self.getHand())

    def getField(self):
        ans = set()
        for card in self.game.zones[Zone.FIELD]:
            if card.controller == self:
                ans.add(card)
        return ans

    def getGrave(self):
        return self.grave

    def getExile(self):
        return self.exile

    def getHand(self):
        return self.hand

    def getDeck(self):
        return self.deck

    def getTopOfDeck(self):
        return self.deck[0]

    def getPlayerID(self):
        return self.playerID

    def getLife(self):
        return self.lifeTotal

    def setLife(self, newTotal):
        self.lifeTotal = newTotal

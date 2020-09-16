from actions.evaluate import isLegal
from actions.trigger import target


class Effect():
    """Structure of effect list:
    [
        [action1, [args1, args2]],
        [action2, [args3, args4]],
        ...
    ]
    """

    def __init__(self):
        self.sourceAbility = None
        self.sourceCard = None
        self.effect = None
        self.rulesText = None
        # [[TargetRestriction1, chosenTargets1],[TargetRestriction2, chosenTargets2]]
        self.targets = []
        self.cost = None

    def addEffect(self, effect):
        """Structure of effect list:
        [
            [action1, [args1, args2]],
            [action2, [args3, args4]],
            ...
        ]
        """
        self.effect += effect


class TargetRestriction():
    def __init__(self, game, rulesText, numRequired=1, doesTarget=False, zones=None, controllers=None, cardTypes=None, tapped=None, untapped=None, instanceID=None, memID=None, cmc=None, power=None, toughness=None, playerIDs=None, gte=None, lte=None, customFunction=None):
        self.game = game
        self.rulesText = rulesText
        self.controllers = controllers
        self.zones = zones  # Zones to check incon

        self.instanceID = instanceID
        self.memID = memID

        self.tapped = tapped
        self.untapped = untapped

        self.gte = gte
        self.lte = lte
        self.cmc = cmc
        self.power = power
        self.toughness = toughness
        self.cardTypes = cardTypes

        self.playerIDs = []

        self.customFunction = customFunction
        self.x = 0
        self.doesTarget = doesTarget
        self.numRequired = numRequired

    def hasController(self, card):
        return True if card.controller in self.controllers else False

    def InZone(self, card):
        return True if card.currentZone in self.zones else False

    def hasInstanceID(self, card):
        return True if card.instanceID == self.instanceID else False

    def hasMemID(self, card):
        return True if card.memID == self.memID else False

    def isTapped(self, card):
        return True if card.tapped else False

    def isUntapped(self, card):
        return False if card.tapped else True

    def hasCMC(self, card):
        if self.gte:
            return True if card.getCMC() > self.cmc else False
        if self.lte:
            return True if card.getCMC() < self.cmc else False

        return True if card.getCMC() == self.cmc else False

    def hasPower(self, card):
        if self.gte:
            return True if card.power > self.power else False
        if self.lte:
            return True if card.power < self.power else False

        return True if card.power == self.power else False

    def hasToughness(self, card):
        if self.gte:
            return True if card.power > self.power else False
        if self.lte:
            return True if card.power < self.power else False

        return True if card.power == self.power else False

    def hasCardTypes(self, card):
        for cardType in self.cardTypes:
            if cardType not in card.cardTypes:
                return False
        return True

    def canTarget(self, card):
        return isLegal(self.game, target, card=card)

    def getLegalTargets(self, game, player):
        selectable = game.allCards.values()

        if self.zones:
            selectable = filter(self.InZone, selectable)

        if self.controllers:
            selectable = filter(self.hasController, selectable)

        if self.cardTypes:
            selectable = filter(self.hasCardTypes, selectable)

        if self.instanceID:
            selectable = filter(self.hasInstanceID, selectable)

        if self.memID:
            selectable = filter(self.hasMemID, selectable)

        if self.tapped:
            selectable = filter(self.isTapped, selectable)

        if self.untapped:
            selectable = filter(self.isUntapped, selectable)

        if self.cmc:
            selectable = filter(self.hasCMC, selectable)

        if self.power:
            selectable = filter(self.hasPower, selectable)

        if self.toughness:
            selectable = filter(self.hasToughness, selectable)

        if self.doesTarget:
            selectable = filter(self.canTarget, selectable)

        return selectable

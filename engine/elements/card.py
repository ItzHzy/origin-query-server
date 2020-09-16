from uuid import uuid1

from consts.counter import Counter
from consts.layer import Layer
from consts.type import Subtype, Supertype, Type


class Card():
    def __init__(self, game, player, oracle):
        self.name = None
        self.game = game
        self.oracle = oracle
        self.instanceID = "C-" + str(uuid1())
        self.owner = player
        self.memID = "M-" + str(uuid1())
        self.finalChapter = None
        self.cardTypes = set()
        self.colors = set()
        self.power = None
        self.toughness = None
        self.controller = player
        self.currentZone = None
        self.abilities = []
        self.counters = {}  # Cleared on reset
        self.attachedTo = None

        self.tapped = False
        self.flipped = False
        self.phasedIn = False
        self.faceUp = False

        self.mainEffect = None
        self.manaCost = {}  # Mana symbols on the card
        self.alternativeCosts = []  # [types  ex. "Flashback", cost, indexOfEffect usually 0]
        self.additionalCosts = []  # [types, cost, indexOfEffect]

        self.cost = None  # Cleared on reset
        self.effect = None  # Cleared on reset

        self.damageMarked = None
        self.attacking = None
        self.blocking = []

        self.isCopy = False
        self.isToken = False

        self.printed = {}
        self.modifiers = {
            Layer.ONE: [],
            Layer.TWO: [],
            Layer.THREE: [],
            Layer.FOUR: [],
            Layer.FIVE: [],
            Layer.SIX: [],
            Layer.SIX_A: [],
            Layer.SIX_B: [],
            Layer.SIX_C: [],
            Layer.SIX_E: []
        }

        self.namedProps = {}  # Cleared on reset
        self.dynamicProps = set()  # Cleared on reset

        game.allCards[self.instanceID] = self

    def hasType(self, kind):
        if kind not in self.cardTypes:
            return False
        return True

    def hasTypes(self, types):
        for kind in types:
            if kind not in self.cardTypes:
                return False
        return True

    def hasKeyword(self, keyword):
        return keyword in self.abilities

    def isPermanent(self):
        if self.hasType(Type.CREATURE) or self.hasType(Type.ENCHANTMENT) or self.hasType(Type.ARTIFACT) or self.hasType(Type.LAND):
            return True
        return False

    def isHistoric(self):
        if self.hasType(Supertype.LEGENDARY) or self.hasType(Type.ARTIFACT) or self.hasType(Subtype.SAGA):
            return True
        return False

    def getCMC(self):
        pass

    def addModifier(self, modifier):
        self.modifiers[modifier["layer"]].append(modifier)
        self.update()

    def removeModifier(self, modifier):
        self.modifiers[modifier["layer"]].remove(modifier)
        self.update()

    def update(self):
        self.name = self.printed["name"]
        self.power = self.printed["power"]
        self.toughness = self.printed["toughness"]
        self.abilities = self.printed["abilities"]
        self.cardTypes = self.printed["types"]
        self.colors = self.printed["colors"]
        self.controller = self.owner

        for change in self.modifiers[Layer.ONE]:
            self.name = change["name"]
            self.power = change["power"]
            self.toughness = change["toughness"]
            self.abilities = change["abilities"]
            self.cardTypes = change["cardTypes"]
            self.colors = change["colors"]

        for change in self.modifiers[Layer.TWO]:
            self.controller = change["player"]

        for change in self.modifiers[Layer.FOUR]:
            if change["isSetting"]:
                self.cardTypes = change["types"]
            else:
                for cardType in change["types"]:
                    self.cardTypes.add(cardType)

        for change in self.modifiers[Layer.FIVE]:
            if change["isSetting"]:
                self.colors = change["colors"]
            else:
                for color in change["colors"]:
                    self.colors.add(color)

        for change in self.modifiers[Layer.SIX]:
            if change["isSetting"]:
                self.abilities = change["abilities"]
            else:
                for ability in change["abilities"]:
                    self.abilities.append(ability)

        for change in self.modifiers[Layer.SIX_A]:
            self.power = change["powerCDF"](self.game, self)
            self.toughness = change["toughnessCDF"](self.game, self)

        for change in self.modifiers[Layer.SIX_B]:
            self.power = change["basePower"]
            self.toughness = change["baseToughness"]

        for change in self.modifiers[Layer.SIX_C]:
            self.power += change["powerDelta"]
            self.toughness += change["toughnessDelta"]

        if Counter.P1P1 in self.counters:
            self.power += self.counters[Counter.P1P1]
            self.toughness += self.counters[Counter.P1P1]
        if Counter.M1M1 in self.counters:
            self.power -= self.counters[Counter.M1M1]
            self.toughness -= self.counters[Counter.M1M1]

        for _ in self.modifiers[Layer.SIX_E]:
            temp = self.power
            self.power = self.toughness
            self.toughness = temp

    def reset(self):
        self.memID = "M-" + str(uuid1())
        self.property = {}
        self.modifiers[Layer.ONE] = []
        self.modifiers[Layer.TWO] = []
        self.modifiers[Layer.THREE] = []
        self.modifiers[Layer.FOUR] = []
        self.modifiers[Layer.FIVE] = []
        self.modifiers[Layer.SIX] = []
        self.modifiers[Layer.SIX_0] = []
        self.modifiers[Layer.SIX_A] = []
        self.modifiers[Layer.SIX_B] = []
        self.modifiers[Layer.SIX_C] = []
        self.modifiers[Layer.SIX_D] = []
        self.modifiers[Layer.SIX_E] = []
        self.tapped = False
        self.flipped = False
        self.phasedIn = False
        self.faceUp = False
        self.counters = {}
        self.damageMarked = 0
        self.effect = None


class MFCard():
    def __init__(self, face1, face2, splitType):
        self.faces = (face1, face2)
        self.splitType = splitType
        self.dominantSide = None

    def reset(self):
        pass

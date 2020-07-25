from enumeratedTypes import *
from gameActions import evaluate, drawCards
from basicFunctions import doPhaseActions, givePriority, goToNextPhase, doAction
from uuid import uuid1
from database import cards_db
from os.path import normpath
from importlib import import_module
from random import shuffle
import json
import asyncio
from preload import sio  # pylint: ignore=import-error


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
        self.field = set()
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

        self.game.AddZone(self, Zone.DECK, self.getDeck())
        self.game.AddZone(self, Zone.FIELD, self.getField())
        self.game.AddZone(self, Zone.GRAVE, self.getGrave())
        self.game.AddZone(self, Zone.EXILE, self.getExile())
        self.game.AddZone(self, Zone.HAND, self.getHand())

    def getField(self):
        return self.field

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


class Card():
    def __init__(self, game, player, oracle):
        self.name = None
        self.game = game
        self.oracle = oracle
        self.instanceID = "C-" + str(uuid1())
        self.memID = "M-" + str(uuid1())
        game.allCards[self.instanceID] = self

        self.cardTypes = set()
        self.colors = set()

        self.cmc = None
        self.manaCost = None  # Mana symbols on the card

        self.mainCosts = []  # [types  ex. "Flashback", cost, indexOfEffect usually 0]
        self.additionalCosts = []  # [types, cost, indexOfEffect]

        self.effect = None  # Cleared on reset

        self.power = None
        self.toughness = None

        self.damageMarked = None
        self.currentZone = None

        self.owner = player
        self.controller = player

        self.effects = []
        self.abilities = []
        self.characteristics = {
            Layer.BASE: None,
            Layer.ONE: [],
            Layer.TWO: [],
            Layer.THREE: [],
            Layer.FOUR: [],
            Layer.FIVE: [],
            Layer.SIX: [],
            Layer.SIX_0: [],
            Layer.SIX_A: [],
            Layer.SIX_B: [],
            Layer.SIX_C: [],
            Layer.SIX_E: []
        }
        self.counters = {}
        self.property = {}  # Cleared on reset
        # Does not clear on reset. Used for things like declareVariable
        self.specialTypes = set()

        self.tapped = False
        self.flipped = False
        self.phasedIn = False
        self.faceUp = False

        self.finalChapter = None

        self.attachedTo = None

        self.isModal = False
        self.maxNumOfChoices = None  # "Choose #"
        self.repeatableChoice = False  # "You may choose the same mode more than once"

        self.isCopy = False
        self.isToken = False

    def getCardTypes(self):
        return self.cardTypes

    def hasTypes(self, types):
        for kind in types:
            if kind not in self.cardTypes:
                return False
        return True

    def hasType(self, kind):
        if kind not in self.cardTypes:
            return False
        return True

    def addCharacteristic(self, layer, item):
        self.characteristics[layer].append(item)

    def updateCharacteristics(self):
        self.game.referenceCard = self
        i = self.characteristics[Layer.BASE]

        self.name = i[0]
        self.power = i[1]
        self.toughness = i[2]
        self.abilities = i[3]
        self.cardTypes = i[4]
        self.colors = i[5]
        self.controller = self.owner

        for i in self.characteristics[Layer.ONE]:
            self.name = i[0]
            self.power = i[1]
            self.toughness = i[2]
            self.abilities = i[3]
            self.cardTypes = i[4]
            self.colors = i[5]

        self.controller = self.owner
        for i in self.characteristics[Layer.TWO]:
            self.controller = i[0]

        for i in self.characteristics[Layer.FOUR]:
            if i[0]:
                for kind in i[1]:
                    self.cardTypes.add(kind)
            else:
                self.cardTypes = i[1]

        for i in self.characteristics[Layer.FIVE]:
            if i[0]:
                for color in i[1]:
                    self.colors.add(color)
            else:
                self.colors = i[1]

        for i in self.characteristics[Layer.SIX]:
            if i[0]:
                for ability in i[1]:
                    self.abilities.append(ability)
            else:
                self.abilities = i[1]

        for i in self.characteristics[Layer.SIX_0]:
            self.abilities.remove(i[0])

        for i in self.characteristics[Layer.SIX_A]:
            self.power = i[0](self.game)
            self.toughness = i[1](self.game)

        for i in self.characteristics[Layer.SIX_B]:
            self.power = i[0]
            self.toughness = i[1]

        for i in self.characteristics[Layer.SIX_C]:
            self.power += i[0]
            self.toughness += i[1]

        if self.hasType(Type.CREATURE):
            if Counter.P1P1 in self.counters:
                self.power += self.counters[Counter.P1P1]
                self.toughness += self.counters[Counter.P1P1]
            if Counter.M1M1 in self.counters:
                self.power -= self.counters[Counter.M1M1]
                self.toughness -= self.counters[Counter.M1M1]

        for i in self.characteristics[Layer.SIX_E]:
            t = self.power
            self.power = self.toughness
            self.toughness = t

    def isAttached(self):
        pass

    def getAttached(self):
        # Returns attached permanent
        pass

    def reset(self):
        self.memID = "M-" + str(uuid1())
        self.property = {}
        self.characteristics[Layer.ONE] = []
        self.characteristics[Layer.TWO] = []
        self.characteristics[Layer.THREE] = []
        self.characteristics[Layer.FOUR] = []
        self.characteristics[Layer.FIVE] = []
        self.characteristics[Layer.SIX] = []
        self.characteristics[Layer.SIX_0] = []
        self.characteristics[Layer.SIX_A] = []
        self.characteristics[Layer.SIX_B] = []
        self.characteristics[Layer.SIX_C] = []
        self.characteristics[Layer.SIX_D] = []
        self.characteristics[Layer.SIX_E] = []
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


class Game():
    def __init__(self, uuid, title, numPlayers, creator, status):
        self.gameID = uuid
        self.title = title
        self.creator = creator
        self.numPlayers = numPlayers
        self.status = status

        self.players = []  # List of all players in a game
        # Used for tokens or cards that don't exist in a deck normally ex. the back half of a DFC
        self.blindingEternities = []
        self.LE = {"Rules": {}, "Allowances": {},
                   "Triggers": {}, "Replacements": {}}  # Lex Magico

        self.zones = {Zone.STACK: []}
        self.allCards = {}
        self.GAT = {}  # Global Ability Table
        self.GMT = {}  # Global Modifier Table
        self.costModifiers = []
        self.trackers = []

        self.activePlayer = None
        self.currPhase = None
        self.priority = None
        self.waitingOn = None
        self.chosenAnswer = None

        self.replacedBy = []

        self.won = False
        self.winners = []

    def getCard(self, instanceID):
        pass

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
        for effect in obj.effect:
            evaluate(self, *effect)

    def push(self, obj):
        pass

    def pop(self):

        self.replacedBy = []
        pass

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

    def addKeywordAbility(self, keyword):
        # Complete in __init__ for ability
        pass

    def addPlayerToGame(self, player):
        self.players.append(player)

    def removePlayerFromGame(self, player):
        self.players.remove(player)

    async def run(self):
        for player in self.players:
            for key in player.cards:
                result = cards_db.find_one(oracle_id=key)
                module_ = import_module(result['filepath'])
                class_ = getattr(module_, result['name'])
                for _ in range(player.cards[key]):
                    card = class_(self, player, key)
                    player.deck.append(card)
                    self.allCards[card.instanceID] = card
            shuffle(player.deck)
            drawCards(self, player, 7)
        await asyncio.sleep(0)

        stack = self.zones[Zone.STACK]
        self.activePlayer = self.players[0]
        self.currPhase = Turn.UNTAP

        while not self.won:
            doPhaseActions(self)
            passedInSuccession = False
            while not passedInSuccession:
                passedInSuccession = True
                for player in self.getRelativePlayerList(self.activePlayer):
                    # checkSBA(self)
                    givePriority(self, player)

                    msg = {"question": "Do action?"}
                    self.notify("Binary Question", msg, player)

                    while player.answer == None:
                        await asyncio.sleep(0)

                    if player.answer:
                        player.answer = None
                        passedInSuccession = False
                        while not player.passed:
                            await doAction(self, player)
            evaluate(self, goToNextPhase)

    def notifyAll(self, event, msg):
        asyncio.create_task(sio.emit(event, msg, room=self.gameID))

    def notify(self, event, msg, player):
        asyncio.create_task(sio.emit(event, msg, player.sid))


class TargetRestriction():
    def __init__(self, game, rulesText):
        self.game = game
        self.rulesText = rulesText
        self.allowedZones = []  # Zones to check in
        self.controller = []
        self.cardTypes = []

        self.tapped = None
        self.untapped = None

        self.cmcGTE = None
        self.cmcLTE = None
        self.cmc = None

        self.powerGTE = None
        self.powerLTE = None
        self.power = None

        self.toughnessGTE = None
        self.toughnessLTE = None
        self.toughness = None

        self.playerID = []
        self.instanceID = []
        self.memID = []
        self.name = None
        self.customFunction = None

        self.x = 0
        self.doesTarget = False
        self.numRequired = 0

    def hasLegalTargets(self, game):
        # Returns True if their are legal targets, False otherwise
        pass

    def getLegalTargets(self, game):
        # Return all legal targets
        pass


class gameListener():  # Used for Triggered Abilties
    def __init__(self, source, listenerFunction, effect):
        self.source = source  # AbilityID of source
        self.listenerFunction = listenerFunction
        self.effect = effect
        self.status = False

    def getSource(self):
        return self.source

    def getFunc(self):
        return self.listenerFunction

    def getEffect(self):
        return self.effect

    def isActive(self):
        return self.status

    def resolveEffect(self):
        # Evaluate every action in the effect with evaluate()
        pass


class GameRule():  # Will return if a action is illegal
    def __init__(self, ruleFunction, source=None, nameOfGameRule=None):
        self.source = source  # AbilityID of source or None if part of base game
        self.ruleFunction = ruleFunction
        self.nameOfGameRule = nameOfGameRule

    def isAllowed(self, targetFunc, targetArgs):
        if self.ruleFunction(targetFunc, targetArgs) == True:
            if self.source is None:
                return GameRuleViolation(self.nameOfGameRule, targetFunc, targetArgs)
            return GameRuleViolation(self.source, targetFunc, targetArgs)
        return GameRuleAns.UNKNOWN


class GameRuleViolation():
    def __init__(self, sourceOfViolation, targetFunc, targetArgs):
        self.sourceOfViolation = sourceOfViolation
        self.targetFunc = targetFunc
        self.targetArgs = targetArgs

    def getSource(self):
        return self.sourceOfViolation

    def getAction(self):
        return self.targetFunc

    def getArgs(self):
        return self.targetArgs


class GameAllowance():
    def __init__(self, ruleFunction, source):
        self.source = None  # AbilityID of source
        self.ruleFunction = ruleFunction

    def isAllowed(self, targetFunc, targetArgs, gameRuleViolation):
        if gameRuleViolation == GameRuleAns.UNKNOWN:
            return GameRuleAns.UNKNOWN
        elif self.ruleFunction(targetFunc, targetArgs, gameRuleViolation) == GameRuleAns.ALLOWED:
            return GameRuleAns.ALLOWED
        else:
            return gameRuleViolation


class ModifierApplier():
    # Chang name to modifier applier
    def __init__(self, modifiersToApply, targetRestriction):
        self.modifiersToApply = modifiersToApply
        self.targetRestriction = targetRestriction

    def apply(self):
        pass


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


class Cost():
    # Only instantiated by addCosts()
    def __init__(self):
        self.manaCost = {}
        self.additional = []

    def canBePaid(self, game, player):
        # Returns True if the cost can be paid by player, False otherwise
        return True  # Temporary

    def pay(self, game, player):
        # Return True if cost is paid, False otherwise
        if self.manaCost != {}:
            pass
        if self.additional != []:
            for cost in self.additional:
                evaluate(game, *cost)
        return True  # Temporary


class CostModifier():
    def __init__(self, cost, costType):
        self.cost = cost
        self.costType = costType
        self.required = False

    def apply(self, obj):
        pass


class Tracker():
    def __init__(self, actionToWatch, argsToWatch, kind="Int", increment=1, resetAtEOT=False, func=None):
        self.actionToWatch = actionToWatch
        self.argsToWatch = argsToWatch
        self.kind = kind
        if kind == "Int":
            self.x = 0
        else:
            self.x = False
        self.increment = increment
        self.resetAtEOT = resetAtEOT
        self.func = func

    def run(self, args):
        i = True
        for index in self.argsToWatch:
            if args[index] != self.argsToWatch[index]:
                i = False
                break
        if i:
            if self.func != None:
                self.func()
            if self.kind == "Int":
                self.x += self.increment
            else:
                self.x = True


class Ability():
    def __init__(self, game, source, allowedZones, rulesText, isManaAbility, keywordName):
        self.source = source
        self.rulesText = rulesText
        self.keywordName = keywordName
        self.abilityID = 'A-' + str(uuid1())
        self.isManaAbility = isManaAbility
        self.allowedZones = allowedZones
        self.specialTypes = set()  # Ex. Variable
        game.GAT[self.abilityID] = self


class ActivatedAbility(Ability):
    def __init__(self, game, source, cost, effect, allowedZones, rulesText, isManaAbility=False, keywordName=None):
        super(ActivatedAbility, self).__init__(game, source,
                                               allowedZones, rulesText, isManaAbility, keywordName)
        self.cost = cost  # cost[0] is a mana cost, cost[1] is for other costs
        self.effect = effect
        self.isActive = False

    def getCost(self):
        return self.cost

    def getEffect(self):
        return self.effect


class TriggeredAbility(Ability):
    # argDict {1: None,
    #          3: self }
    #   check the arg at index in the evaluated function and see if its equal to the value
    def __init__(self, game, source, triggerFunction, argDict, effect, allowedZones, rulesText, isManaAbility=False, keywordName=None):
        super(TriggeredAbility, self).__init__(game, source,
                                               allowedZones, rulesText, isManaAbility, keywordName)
        self.triggerFunction = triggerFunction
        self.argDict = argDict
        self.effect = effect
        self.isActive = False

from enumeratedTypes import *
import gameActions
import basicFunctions
from uuid import uuid1
from database import cards_db
from os.path import normpath
from importlib import import_module
from random import shuffle
import json
import asyncio
from preload import sio  # pylint: disable=import-error


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

        self.printed = None
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
        self.attributes[modifier["layer"]].append(modifier)
        self.update()

    def removeModifier(self, modifier):
        self.attributes[modifier["layer"]].remove(modifier)
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

        for switch in self.modifiers[Layer.SIX_E]:
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
        if gte:
            return True if card.getCMC() > self.cmc else False
        if lte:
            return True if card.getCMC() < self.cmc else False

        return True if card.getCMC() == self.cmc else False

    def hasPower(self, card):
        if gte:
            return True if card.power > self.power else False
        if lte:
            return True if card.power < self.power else False

        return True if card.power == self.power else False

    def hasToughness(self, card):
        if gte:
            return True if card.power > self.power else False
        if lte:
            return True if card.power < self.power else False

        return True if card.power == self.power else False

    def hasCardTypes(self, card):
        for cardType in self.cardTypes:
            if cardType not in card.cardTypes:
                return False
        return True

    def canTarget(self, card):
        return gameActions.isLegal(game, target, card=card)

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
        # TODO: implement canBePaid
        return True

    async def pay(self, game, player):

        convertStringToColorEnum = {
            "Color.WHITE": Color.WHITE,
            "Color.BLUE": Color.BLUE,
            "Color.BLACK": Color.BLACK,
            "Color.RED": Color.RED,
            "Color.GREEN": Color.GREEN,
            "Color.COLORLESS": Color.COLORLESS
        }

        if self.manaCost != {}:
            while True:
                player.answer = None

                game.notify("Pay Mana", {
                    "gameID": game.gameID,
                    "status": "PAYING_MANA",
                    "cost": {
                        "ManaType.GENERIC": self.manaCost[ManaType.GENERIC] if ManaType.GENERIC in self.manaCost else 0,
                        "ManaType.WHITE": self.manaCost[ManaType.WHITE] if ManaType.WHITE in self.manaCost else 0,
                        "ManaType.BLUE": self.manaCost[ManaType.BLUE] if ManaType.BLUE in self.manaCost else 0,
                        "ManaType.BLACK": self.manaCost[ManaType.BLACK] if ManaType.BLACK in self.manaCost else 0,
                        "ManaType.RED": self.manaCost[ManaType.RED] if ManaType.RED in self.manaCost else 0,
                        "ManaType.GREEN": self.manaCost[ManaType.GREEN] if ManaType.GREEN in self.manaCost else 0,
                        "ManaType.COLORLESS": self.manaCost[ManaType.COLORLESS] if ManaType.COLORLESS in self.manaCost else 0,
                    }
                }, player)

                while player.answer == None:
                    await asyncio.sleep(0)

                # TODO: implement validation of payment

                for color in player.answer:
                    if player.answer[color] > 0:
                        gameActions.evaluate(
                            game, gameActions.removeMana, player, convertStringToColorEnum[color], player.answer[color])

                break

        if self.additional != []:
            for cost in self.additional:
                gameActions.evaluate(game, **cost)

        return True


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
    """Base class for all abilites.

    Attributes:
        game (Game): Game object associated with this ability.
        source (str): InstanceID of the card this ability originates from.
        rulesText (str): Oracle text of this ability
        allowedZones (set(Zone)): Zones where the source needs to be in order to use this ability.
        isManaAbility (bool): Whether or not this ability is a mana ability.
        keyword (Keyword or None): Is set if the ability is a keyword.
        isActive (bool): Whether or not this ability is active.
    """

    def __init__(self, game, source, rulesText, allowedZones, isManaAbility, keyword):
        self.game = game
        self.source = source
        self.rulesText = rulesText
        self.keyword = keyword
        self.abilityID = 'A-' + str(uuid1())
        self.isManaAbility = isManaAbility
        self.allowedZones = allowedZones

        self.isActive = False
        game.GAT[self.abilityID] = self

    def getSource(self):
        return game.allCards[self.source]


class ActivatedAbility(Ability):
    """Class for activated abilites.

    Attributes

    """

    def __init__(self, game, source, rulesText, cost, effect, allowedZones={Zone.FIELD}, isManaAbility=False, keyword=None):
        super(ActivatedAbility, self).__init__(game, source, rulesText, allowedZones, isManaAbility, keyword)
        self.cost = cost
        self.effect = effect


class TriggeredAbility(Ability):
    """
    """

    def __init__(self, game, source, rulesText, action, triggerFunc, effect, interveningIf=None, allowedZones={Zone.FIELD}, isManaAbility=False, keyword=None):
        super(TriggeredAbility, self).__init__(game, source, rulesText, allowedZones, isManaAbility, keyword)
        self.action = action
        self.triggerFunc = triggerFunc
        self.effect = effect
        self.interveningIf = interveningIf

        if action.__name__ in game.triggers:
            game.triggers[action].append(self)
        else:
            game.triggers[action] = [self]

    def triggers(action, **params):
        """Determines if the action being taken will trigger this ability

        Args: 
            action (function): Action being taken
            params (dict): Parameters for the above action

        Returns:
            Bool: True if action will trigger this ability, False otherwise
        """
        if triggerFunc(action, **params):
            if self.interveningIf and self.interveningIf(actionBeingDone, **params):
                return True
        return False

    def trigger(action, **params):
        """Returns 
        """
        pass

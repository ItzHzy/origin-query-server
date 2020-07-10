from enumeratedTypes import * 
from uuid import uuid1
from database import cards_db

class Player():
    def __init__(self, game, name, ws):
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
        self.manaPool = {Color.WHITE: 0, Color.BLUE: 0, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0, Color.COLORLESS: 0}

        self.passed = False
        self.awaitingTriggers = []

        self.hasSplice= False

        self.isHost = False
        self.ws = ws
        self.cards = None
        self.cardObjs = []
        self.isReady = False

    def playerInit(self):
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
        self.deck[0]

    def getPlayerID(self):
        return self.playerID

    def getLife(self):
        return self.lifeTotal

    def setLife(self, newTotal):
        self.lifeTotal = newTotal

class Card():
    def __init__(self, game, player):
        self.name = None
        self.game = game
        self.instanceID = game.getNewInstanceID()
        self.memID = None
        game.allCards[self.instanceID] = self

        self.cardTypes = set()
        self.colors = set()

        self.cmc = None
        self.manaCost = None # Mana symbols on the card
        
        self.mainCosts = [] # [types  ex. "Flashback", cost, indexOfEffect usually 0]
        self.additionalCosts = [] # [types, cost, indexOfEffect]

        self.effect = None # Cleared on reset

        self.power = None
        self.toughness = None

        self.damageMarked = None
        self.currentZone = None

        self.owner = player
        self.controller = None

        self.effects = []
        self.abilities = []
        self.characteristics = {
            Layer.BASE : None,
            Layer.ONE  : [],
            Layer.TWO  : [],
            Layer.THREE: [],
            Layer.FOUR : [],
            Layer.FIVE : [],
            Layer.SIX  : [],
            Layer.SIX_0: [],
            Layer.SIX_A: [],
            Layer.SIX_B: [],
            Layer.SIX_C: [],
            Layer.SIX_E: []
        }
        self.counters = {}
        self.property = {} # Cleared on reset
        self.specialTypes = set() # Does not clear on reset. Used for things like declareVariable

        self.tapped = False
        self.flipped = False
        self.phasedIn = False
        self.faceUp = False

        self.finalChapter = None

        self.attachedTo = None

        self.isModal = False
        self.maxNumOfChoices = None # "Choose #"
        self.repeatableChoice = False # "You may choose the same mode more than once"

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

    def getInstanceID(self):
        return self.instanceID

    def getMemID(self):
        return self.memID

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

    def getName(self):
        return self.name

    def getController(self):
        return self.controller

    def getOwner(self):
        return self.owner

    def getPower(self):
        return self.power

    def getToughness(self):
        return self.toughness

    def getLoyalty(self):
        return self.counters[Counter.LOYALTY]

    def isAttached(self):
        pass

    def getAttached(self):
        # Returns attached permanent
        pass

    def reset(self):
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
        self.playersDict = {} # Used for turn order
        self.blindingEternities = []  # Used for tokens or cards that don't exist in a deck normally ex. the back half of a DFC
        self.LE = {}  # Lex Magico
        self.stack = []

        self.zones = {}
        self.allCards = {}
        self.GAT = set() # Global Ability Table
        self.GMT = set() # Global Modifier Table
        self.costModifiers = []
        self.trackers = []

        self.instanceIDPool = 0
        self.playerIDPool = 0
        self.LinkedIDPool = 0
        self.memIDPool = 0
        self.abilityIDPool = 0
        self.modifierIDPool = 0

        self.activePlayer = None
        self.currPhase = None

        self.replacedBy = []

        # Used temporarily as pseudo globals by various functions
        self.referencePlayer = None 
        self.referenceCard = None
        self.referenceEffect = None

        self.won = False
        self.winners = []

        # for index, player in enumerate(self.players):
        #     if player != self.players[-1]:
        #         self.playersDict[player] = self.players[index + 1]
        # self.playersDict[self.players[-1]] = self.players[0]

    def getNewPlayerID(self):
        self.playerIDPool += 1
        return self.playerIDPool

    def getNewLinkedID(self):
        self.LinkedIDPool += 1
        return self.LinkedIDPool

    def getNewMemID(self):
        self.memIDPool += 1
        return self.memIDPool

    def getNewAbilityID(self):
        self.abilityIDPool += 1
        return self.abilityIDPool

    def getNewModiferID(self):
        self.modifierIDPool += 1
        return self.modifierIDPool

    def getNewInstanceID(self):
        self.instanceIDPool += 1
        return self.instanceIDPool

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

    def push(self, obj):
        if (isinstance(obj, Card)):
            pass
        elif (isinstance(obj, Effect)):
            pass

    def pop(self):
        self.replacedBy = []
        pass

    def getActivePlayer(self):
        return self.activePlayer

    def getNextPlayer(self, player):
        return self.playersDict[player]

    def getRelativePlayerList(self, player):
        # This took me an hour to come up with 🤫
        
        lst = []
        lastPlayerChecked = player
        i = True
        while lastPlayerChecked != player and i:
            if i:
                lst.append(player)
                i = False
            lst.append(self.playersDict[player])
            lastPlayerChecked = self.playersDict[player]
        
        return lst

    def addKeywordAbility(self, keyword):
        pass

    def addPlayerToGame(self, player):
        self.players.append(player)
        
    def removePlayerFromGame(self, player):
        self.players.remove(player)

    def prep(self):
        for player in self.players:
            for key in player.cards:
                result = cards_db.find_one(oracle_id=key)
                module_ = __import__(result['filepath'])
                class_ = getattr(module_, result['name'])
                for _ in range(player.cards[key]):
                    player.cardObjs.append(class_(self, player))
                    

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

    def __deepcopy__(self, arg):
        # Overides deepcopy in order to imitate eager evaluation and return chosen legal targets
        from gameActions import choose
        x = choose(self.getLegalTargets(self.game), self.game.referencePlayer, InquiryType.TARGET, self.numRequired)
        self.game.referenceEffect.targets += [[self, x]]
        return x

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
        #Evaluate every action in the effect with evaluate()
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
    def __init__(self, source):
        self.source = source
        self.effect = None
        self.rulesText = None
        self.targets = [] # [[TargetRestriction1, chosenTargets1],[TargetRestriction2, chosenTargets2]]
        self.cost = None

    def getText(self):
        return self.rulesText

    def getSource(self):
        return self.source

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
        pass

    def pay(self, game, player):
        pass

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

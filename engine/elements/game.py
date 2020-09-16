import asyncio
from importlib import import_module
from random import shuffle

from actions.evaluate import evaluate
from actions.player import activateAbility, cast, playLand
from actions.turn import doPhaseActions, givePriority, goToNextPhase
from actions.zone import drawCards, moveToZone
from consts.turn import Turn
from consts.type import Type
from consts.zone import Zone
from database import cards_db
from elements.card import Card
from elements.cost import addCosts
from elements.effect import Effect


class self():
    def __init__(self, uuid, title, numPlayers, creator, status):
        self.gameID = uuid
        self.title = title
        self.creator = creator
        self.numPlayers = numPlayers
        self.status = status

        self.players = []  # List of all players in a self

        self.rules = {}  # store all self rules
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
            evaluate(self, moveToZone, obj, Zone.FIELD, None)
        else:
            for effect in obj.effect:
                evaluate(self, **effect)

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

    def addPlayerToself(self, player):
        self.players.append(player)

    def removePlayerFromself(self, player):
        self.players.remove(player)

    async def doAction(self, player):
        # waits for the player to make a choice
        player.passed = False
        player.chosenAction = None
        self.waitingOn = player

        while True:

            player.chosenAction = None
            while player.chosenAction == None and player.passed == False:
                await asyncio.sleep(0)

            if player.passed:
                self.notify("Lose Priority", {
                    "selfID": self.gameID
                }, player)

                break

            else:
                self.passedInSuccession = False
                choice = player.chosenAction
                if choice[0] == 'C':
                    card = self.allCards[choice]
                    if card.hasType(Type.LAND):
                        evaluate(self, playLand, card=card, player=player)
                    else:
                        await self.declareCast(self, choice, player)
                elif choice[0] == 'A':
                    await self.declareActivation(self, choice)

    async def declareCast(self, instanceID, player):
        card = self.getCard(instanceID)
        allEffects = card.effects.copy()  # copy of all effects on the card

        chosenMainCost = {}
        chosenAddedCosts = []
        chosenEffects = []  # chosen effects
        effectIndexesAdded = []  # indexes of the effects added from allEffects
        effectTypes = set()  # Effect

        result = Effect()
        result.sourceCard = card

        # # Used for modal spells
        # if card.isModal:
        #     effectIndexesAdded.append(0)
        #     num = card.maxNumOfChoices
        #     effectList = []
        #     for effect in allEffects[0]:
        #         if card.repeatableChoice:
        #             for _ in range(num):
        #                 effectList.append(effect)
        #         else:
        #             effectList.append(effect)
        #     chosenEffects.append(
        #         choose(self, effectList, player, InquiryType.MODAL, effectList.append(effect)))

        # # Chose what x should be
        # if Keyword.DECLARE_VAR in card.specialTypes:
        #     card.property["X"] = choose(
        #         self, None, player, InquiryType.VARIABLE, 1)

        # Choose main cost or alt cost if applicable and add their respective effect
        if len(card.alternativeCosts) > 0:
            pass
        else:
            chosenMainCost = card.manaCost

        # Add chosen additional costs and their respective effects
        if len(card.additionalCosts) > 0:
            pass

        # Add all chosen effect to result.effect
        for effect in chosenEffects:
            result.addEffect(effect[1])

        # Add all the rules text for the chosen effects to result.rulesText
        for effect in chosenEffects:
            result.rulesText += " " + effect[0]

        # Instantiate a cost object with the chosen costs and set it in result.cost
        card.cost = addCosts(self, card, chosenMainCost, chosenAddedCosts)

        # Add cost types to card properties like Flashback
        for costType in effectTypes:
            card.property[costType] = True

        # Evaluate cast
        if card.cost.canBePaid(self, card.controller):
            if await card.cost.pay(self, card.controller):
                evaluate(self, cast, card=card)

    async def declareActivation(self, abilityID):
        ability = self.GAT[abilityID]
        result = Effect()
        result.effect = ability.effect.copy()
        result.sourceAbility = ability
        result.sourceCard = ability.source
        result.cost = addCosts(self, ability, ability.cost[0], ability.cost[1])
        result.rulesText = ability.rulesText

        if result.cost.canBePaid(self, result.sourceCard.controller):
            if await result.cost.pay(self, result.sourceCard.controller):
                evaluate(self, activateAbility, effect=result)

    async def askBinaryQuestion(self, msg, player):
        player.answer = None
        self.notify("Binary Question", {"selfID": self.gameID, "msg": msg}, player)

        try:
            while player.answer == None:
                await asyncio.sleep(0)
        finally:
            return player.answer

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
                "selfID": self.gameID,
                "playerID": player.playerID,
                "zoneType": "Zone.DECK",
                "num": len(player.deck)
            }

            self.notifyAll("Zone Size Update", msg3)

            self.notifyAll("Life Total Update", {
                "selfID": self.gameID,
                "playerID": player.playerID,
                "life": player.lifeTotal
            })

            # each player draws seven cards
            drawCards(self, player, 7)

        # let the current task sleep so that the messages emitted during setup can go through
        await asyncio.sleep(0)

    async def run(self):
        self.currPhase = Turn.UNTAP
        self.activePlayer = self.players[0]

        # Use try except to check for win

        while not self.won:  # main selfplay loop
            await doPhaseActions(self)
            self.passedInSuccession = False
            while not self.passedInSuccession and (self.currPhase != Turn.UNTAP or (self.currPhase == Turn.CLEANUP and self.zones[Zone.STACK] != [])):
                self.passedInSuccession = True
                for player in self.getRelativePlayerList(self.activePlayer):
                    # checkSBA(self)
                    givePriority(self, player)
                    await self.doAction(self, player)

            if self.zones[Zone.STACK] != []:
                self.pop()
            else:
                evaluate(self, goToNextPhase)

    def notifyAll(self, event, msg):
        asyncio.create_task(sio.emit(event, msg, room=self.gameID))

    def notify(self, event, msg, player):
        asyncio.create_task(sio.emit(event, msg, player.sid))

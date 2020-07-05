from enumeratedTypes import * # pylint: disable=unused-wildcard-import
from gameElements import * # pylint: disable=unused-wildcard-import
from movingZones import * # pylint: disable=unused-wildcard-import
from combatFunctions import * # pylint: disable=unused-wildcard-import
from gameActions import * # pylint: disable=unused-wildcard-import
from copy import deepcopy

def doPhaseActions(game):
    currPhase = game.GD("Current Phase")
    activePlayer = game.GD("Active Player")

    if currPhase == Turn.UNTAP:
        phaseIn(game, activePlayer)
        checkSBA(game)
        untapAll(game, activePlayer)
    elif currPhase == Turn.UPKEEP:
        phaseIn(game, activePlayer)
        checkModifiers(game)
    elif currPhase == Turn.DRAW:
        evaluate(game, drawCard, activePlayer)
    elif currPhase == Turn.DECLARE_ATTACKS:
        chooseAttackers(game, activePlayer)
    elif currPhase == Turn.DECLARE_BLOCKS:
        for player in game.players:
            if player != activePlayer:
                chooseBlockers(game, player)
    elif currPhase == Turn.FIRST_COMBAT_DAMAGE:
        resolveCombatMatrix_FS(game)
    elif currPhase == Turn.SECOND_COMBAT_DAMAGE:
        resolveCombatMatrix(game)
    elif currPhase == Turn.CLEANUP:
        discardToHandSize(game, activePlayer)
        removeAllDamage(game)
        #Check for SBAs and complete loop rule 514       

nextPhase = { 
    Turn.UNTAP : Turn.UPKEEP,
    Turn.UPKEEP : Turn.DRAW,
    Turn.DRAW : Turn.FIRST_MAIN,
    Turn.FIRST_MAIN : Turn.BEGIN_COMBAT,
    Turn.BEGIN_COMBAT : Turn.DECLARE_ATTACKS,
    Turn.DECLARE_ATTACKS : Turn.DECLARE_BLOCKS,
    Turn.DECLARE_BLOCKS : Turn.FIRST_COMBAT_DAMAGE,
    Turn.FIRST_COMBAT_DAMAGE : Turn.SECOND_COMBAT_DAMAGE,
    Turn.SECOND_COMBAT_DAMAGE : Turn.END_COMBAT,
    Turn.END_COMBAT : Turn.SECOND_MAIN,
    Turn.SECOND_MAIN : Turn.BEGIN_END,
    Turn.BEGIN_END : Turn.CLEANUP }

def goToNextPhase(game):
    currPhase = game.currPhase
    activePlayer = game.activePlayer

    evaluate(game, endPhase, activePlayer, currPhase)
    if currPhase == Turn.CLEANUP and Turn.EXTRA in activePlayer.property and activePlayer.property[Turn.EXTRA] > 0:
        activePlayer.property[Turn.EXTRA] -= 1
        evaluate(game, beginPhase, activePlayer, Turn.UNTAP)
    elif currPhase == Turn.CLEANUP:
        evaluate(game, beginPhase, game.getNextPlayer(activePlayer), Turn.UNTAP)
    elif currPhase in activePlayer.property and activePlayer.property[currPhase] > 0:
        activePlayer.property[currPhase] -= 1
        evaluate(game, beginPhase, activePlayer, currPhase)
    else:
        evaluate(game, beginPhase, activePlayer, nextPhase[currPhase]) # pylint: disable=unsubscriptable-object

def givePriority(game, player):
    checkSBA(game)
    game.SD("Priority", player)

def checkSBA(game):
    sbaTaken = True
    namesChecked = set()
    cardsToBeDestroyed = set()
    cardsToBeSacrificed = set()
    legendRuled = set()
    diedToSBA = set()

    while(sbaTaken):
        sbaTaken = False
        for player in game.players:
            if player.getLife() <= 0:
                ans = evaluate(game, lose, player, COD.HAVING_0_LIFE)
                if ans != GameRuleAns.DENIED:
                    sbaTaken = True
            elif player.property[COD.DREW_FROM_EMPTY_DECK] == True:
                ans = evaluate(game, lose, player, COD.DREW_FROM_EMPTY_DECK)
                if ans != GameRuleAns.DENIED:
                    sbaTaken = True
            elif player.counters[Counter.POISON] >= 10:
                ans = evaluate(game, lose, player, COD.POISON)
                if ans != GameRuleAns.DENIED:
                    sbaTaken = True
            for permanent in set(player.getField()):
                if permanent not in diedToSBA and permanent not in legendRuled and permanent not in cardsToBeDestroyed and permanent not in permanent not in diedToSBA:
                    if permanent.hasType(Type.CREATURE):
                        if permanent.getToughness() <= 0:
                            diedToSBA.add(permanent)
                            sbaTaken = True
                        elif permanent.damageMarked >= permanent.getToughness():
                            cardsToBeDestroyed.add(permanent)
                            sbaTaken = True
                        elif permanent.property["Deathtouched"]:
                            cardsToBeDestroyed.add(permanent)
                            sbaTaken = True
                        elif permanent.isAttached():
                            unattach(game, permanent, permanent.getAttached())
                            sbaTaken = True
                    elif permanent.hasType(Type.PLANESWALKER):
                        if permanent.getLoyalty() <= 0:
                            diedToSBA.add(permanent)
                            sbaTaken = True
                    elif permanent.hasType(Subtype.AURA):
                        if not verifyAttachment(game, permanent):
                            diedToSBA.add(permanent)
                            sbaTaken = True
                    elif permanent.hasType(Subtype.EQUIPTMENT):
                        if not verifyAttachment(game, permanent):
                            unattach(game, permanent, permanent.getAttached())
                            sbaTaken = True
                    elif permanent.isAttached() and not permanent.hasType(Subtype.AURA) and not permanent.hasType(Subtype.EQUIPTMENT):
                        unattach(game, permanent, permanent.getAttached())
                        sbaTaken = True
                    elif permanent.hasType(Subtype.SAGA):
                        if permanent.counters[Counter.LORE] >= permanent.finalChapter:
                            cardsToBeSacrificed.add(permanent)
                            sbaTaken = True
                    elif permanent.hasType(Supertype.LEGENDARY):
                        name = permanent.getName()
                        if name not in namesChecked:
                            namesChecked.add(name)
                            x = set()
                            for card in set(player.getField()):
                                if card.getName() == permanent.getName() and card.hasType(Supertype.LEGENDARY):
                                    x.add(card)
                            if not (len(x) <= 1):
                                legendRuled.add(x)
                                sbaTaken = True
                    elif permanent.counters[Counter.P1P1] > 0 and permanent.counters[Counter.M1M1] > 0:
                        if permanent.counters[Counter.P1P1] > permanent.counters[Counter.M1M1]:
                            permanent.counters[Counter.P1P1] = permanent.counters[Counter.P1P1] - permanent.counters[Counter.M1M1]
                            permanent.counters[Counter.M1M1] = 0
                        else:
                            permanent.counters[Counter.M1M1] = permanent.counters[Counter.M1M1] - permanent.counters[Counter.P1P1]
                            permanent.counters[Counter.P1P1] = 0
                        sbaTaken = True
    for cards in legendRuled:
        diedToSBA.add(enactLegendRule(game, cards))
    
    for card in cardsToBeSacrificed:
        if not isReplaced(game, fieldToGrave, card):
            evaluate(game, sacrifice, COD.SBA, card)
    for card in diedToSBA:
        if not isReplaced(game, fieldToGrave, card):
            evaluate(game, dies, card)
    for card in cardsToBeDestroyed:
        if not isReplaced(game, fieldToGrave, card):
            evaluate(game, destroy, card)

    for card in cardsToBeSacrificed:
        evaluate(game, fieldToGrave, card)
    for card in cardsToBeDestroyed:
        evaluate(game, fieldToGrave, card)
    for card in diedToSBA:
        evaluate(game, fieldToGrave, card)
   
def verifyLegendStatus(game, player):
    pass

def enactLegendRule(game, cards):
    # returns the set of cards to be removed selected by the player
    pass

def verifyAttachment(game, card):
    #Returns True on legal attachment False on illegal attachment
    pass

def addCosts(game, obj, mainCost, additionalCosts):
    """Used to add up all costs and discounts for a spell or ability

    Args:
        game(Game): Game Object
        obj(Card or Ability): The card or ability being paid
        mainCost(List): List of the forms:
            [True, [mana]] 
            or 
            [False, [[action1, arg11], 
            [action2, arg2], 
            ...]] 
        additionalCosts(List(List)): Lists of the same form as mainCost
        
    Returns:
        totalCost(Cost): The combined costs and discounts of everything 
    """
    totalCost = Cost()
    totalMana = {}  

    if mainCost[0]:
        for manaType in mainCost[1]:
            amount = mainCost[1][manaType]
            totalMana = addCost(manaType, amount, totalMana)
    else:
        for cost in mainCost[1]:
            totalCost.additional.append(cost)
    
    if additionalCosts != None:
        for addedCost in additionalCosts:
            if mainCost[0]:
                for manaType in addedCost[1]:
                    amount = addedCost[1][manaType]
                    totalMana = addCost(manaType, amount, totalMana)
            else:
                for cost in addedCost[1]:
                    totalCost.additional.append(cost)

    return totalCost

def addCost(manaType, amount, currentCost):
    """Called by addCosts to add mana costs together
    """
    if manaType in currentCost:
        currentCost[manaType] += amount
        if currentCost[manaType] <= 0:
            del currentCost[manaType]
    else:
        currentCost[manaType] = amount
    
    return currentCost

def doSomething(game, player):
    # waits for the player to make a choice
    pass

def declareCast(game, instanceID, player):
    card = game.getCard(instanceID)
    allEffects = deepcopy(card.effects) # A copy of all effects on the card

    chosenEffects = [] # Chosen effects
    effectIndexesAdded = [] # indexes of the effects added from allEffects

    mainCost = None
    addedCosts = None

    result = Effect(card)

    game.referenceEffect = result
    game.referencePlayer = player
    game.referenceCard = card

    # Used for modal spells
    if card.isModal:
        effectIndexesAdded.append(0)
        num = card.maxNumOfChoices
        effectList = []
        for effect in allEffects[0]:
            if card.repeatableChoice:
                for i in range(num): # pylint: disable=unused-variable
                    effectList.append(effect)
            else:
                effectList.append(effect)
        chosenEffects.append(choose(effectList, player, InquiryType.MODAL, effectList.append(effect)))

    # Chose what x should be 
    if Keyword.DECLARE_VAR in card.specialTypes:
        card.property["X"] = choose(None, player, InquiryType.VARIABLE, 1)

    # Choose main cost or alt cost if applicable and add their respective effect
    if len(card.mainCosts) > 1:
        c = choose(card.mainCosts, player, InquiryType.MAIN_COST, 1)
        index = c[3] # index of effect associated with the chosen cost
        if not (index in effectIndexesAdded):
            effectIndexesAdded.append(index)
            chosenEffects.append(allEffects[index])
        mainCost = c
    else:
        mainCost = card.mainCosts[0]
        index = card.mainCosts[0][3]
        if not (index in effectIndexesAdded):
            effectIndexesAdded.append(index)
            chosenEffects.append(allEffects[index])

    # Add chosen additional costs and their respective effects
    addedCosts = choose(card.additionalCosts, player, InquiryType.ADD_COST, None)
    
    # Add all chosen effect to result.effect
    for effect in chosenEffects:
        result.addEffect(effect[1])

    # Add all the rules text for the chosen effects to result.rulesText
    for effect in chosenEffects:
        result.rulesText += " " + effect[0]

    # Instantiate a cost object with the chosen costs and set it in result.cost
    result.cost = addCosts(game, card, mainCost[1], [item[1] for item in addedCosts])

    # Add cost types to card properties like Flashback
    for costType in mainCost[0]:
        card.property[costType] = True
    for cost in addedCosts:
        for costType in cost[0]:
            card.property[costType] = True

    # Evaluate cast
    evaluate(game, cast, card)

def decideSplice(card):
    pass

def resolve(game, obj):
    for action in obj.effect:
        if len(action[1]) == 0:
            evaluate(game, action[0])
        elif len(action[1]) == 1:
            evaluate(game, action[0], action[1][0])
        elif len(action[1]) == 2:
            evaluate(game, action[0], action[1][0], action[1][1])
        elif len(action[1]) == 3:
            evaluate(game, action[0], action[1][0], action[1][1], action[1][2])
        elif len(action[1]) == 4:
            evaluate(game, action[0], action[1][0], action[1][1], action[1][2], action[1][3])
        elif len(action[1]) == 5:
            evaluate(game, action[0], action[1][0], action[1][1], action[1][2], action[1][3], action[1][4])

def checkModifiers(game):
    pass 

def winnerDecided(game):
    if game.globalDict["Winners"] != []:
        return True
    return False





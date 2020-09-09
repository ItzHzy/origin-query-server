from enumeratedTypes import *
import gameElements
import gameActions
import combatFunctions
import asyncio


async def doPhaseActions(game):
    currPhase = game.currPhase
    activePlayer = game.activePlayer
    print(currPhase)

    if currPhase == Turn.UNTAP:
        gameActions.phaseIn(game, activePlayer)
        # checkSBA(game)
        gameActions.untapAll(game, activePlayer)
    elif currPhase == Turn.UPKEEP:
        gameActions.phaseIn(game, activePlayer)
    elif currPhase == Turn.DRAW:
        gameActions.evaluate(game, gameActions.drawCard, activePlayer)
    elif currPhase == Turn.DECLARE_ATTACKS:
        await combatFunctions.chooseAttackers(game, activePlayer)
    elif currPhase == Turn.DECLARE_BLOCKS:
        for player in game.getOpponents(activePlayer):
            if player.isDefending:
                await combatFunctions.chooseBlockers(game, player)
    elif currPhase == Turn.FIRST_COMBAT_DAMAGE:
        combatFunctions.resolveCombatMatrix_FS(game)
    elif currPhase == Turn.SECOND_COMBAT_DAMAGE:
        combatFunctions.resolveCombatMatrix(game)
    elif currPhase == Turn.CLEANUP:
        gameActions.discardToHandSize(game, activePlayer)
        combatFunctions.removeAllDamage(game)
        # Check for SBAs and complete loop rule 514


nextPhase = {
    Turn.UNTAP: Turn.UPKEEP,
    Turn.UPKEEP: Turn.DRAW,
    Turn.DRAW: Turn.FIRST_MAIN,
    Turn.FIRST_MAIN: Turn.BEGIN_COMBAT,
    Turn.BEGIN_COMBAT: Turn.DECLARE_ATTACKS,
    Turn.DECLARE_ATTACKS: Turn.DECLARE_BLOCKS,
    Turn.DECLARE_BLOCKS: Turn.FIRST_COMBAT_DAMAGE,
    Turn.FIRST_COMBAT_DAMAGE: Turn.SECOND_COMBAT_DAMAGE,
    Turn.SECOND_COMBAT_DAMAGE: Turn.END_COMBAT,
    Turn.END_COMBAT: Turn.SECOND_MAIN,
    Turn.SECOND_MAIN: Turn.BEGIN_END,
    Turn.BEGIN_END: Turn.CLEANUP}


def goToNextPhase(game):
    currPhase = game.currPhase
    activePlayer = game.activePlayer

    gameActions.evaluate(game, gameActions.endPhase, activePlayer, currPhase)
    if currPhase == Turn.CLEANUP and Turn.EXTRA in activePlayer.property and activePlayer.property[Turn.EXTRA] > 0:
        activePlayer.property[Turn.EXTRA] -= 1
        gameActions.evaluate(game, gameActions.beginPhase,
                             activePlayer, Turn.UNTAP)

    elif currPhase == Turn.CLEANUP:
        nextPlayer = game.getNextPlayer(activePlayer)
        gameActions.evaluate(game, gameActions.beginPhase,
                             nextPlayer, Turn.UNTAP)

    elif currPhase in activePlayer.property and activePlayer.property[currPhase] > 0:
        activePlayer.property[currPhase] -= 1
        gameActions.evaluate(game, gameActions.beginPhase,
                             activePlayer, currPhase)

    elif currPhase == Turn.DECLARE_ATTACKS and game.COMBAT_MATRIX == {}:
        gameActions.evaluate(game, gameActions.beginPhase,
                             activePlayer, Turn.END_COMBAT)
    else:
        gameActions.evaluate(game, gameActions.beginPhase, activePlayer,
                             nextPhase[currPhase])  # pylint: disable=unsubscriptable-object


def givePriority(game, player):
    # checkSBA(game)
    game.priority = player

    game.notify("Give Priority", {
        "gameID": game.gameID
    }, player)


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
                ans = gameActions.evaluate(
                    game, gameActions.lose, player, COD.HAVING_0_LIFE)
                if ans != GameRuleAns.DENIED:
                    sbaTaken = True
            elif player.property[COD.DREW_FROM_EMPTY_DECK] == True:
                ans = gameActions.evaluate(
                    game, gameActions.lose, player, COD.DREW_FROM_EMPTY_DECK)
                if ans != GameRuleAns.DENIED:
                    sbaTaken = True
            elif player.counters[Counter.POISON] >= 10:
                ans = gameActions.evaluate(
                    game, gameActions.lose, player, COD.POISON)
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
                            gameActions.unattach(
                                game, permanent, permanent.getAttached())
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
                            gameActions.unattach(
                                game, permanent, permanent.getAttached())
                            sbaTaken = True
                    elif permanent.isAttached() and not permanent.hasType(Subtype.AURA) and not permanent.hasType(Subtype.EQUIPTMENT):
                        gameActions.unattach(
                            game, permanent, permanent.getAttached())
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
                            permanent.counters[Counter.P1P1] = permanent.counters[Counter.P1P1] - \
                                permanent.counters[Counter.M1M1]
                            permanent.counters[Counter.M1M1] = 0
                        else:
                            permanent.counters[Counter.M1M1] = permanent.counters[Counter.M1M1] - \
                                permanent.counters[Counter.P1P1]
                            permanent.counters[Counter.P1P1] = 0
                        sbaTaken = True
    for cards in legendRuled:
        diedToSBA.add(enactLegendRule(game, cards))

    # for card in cardsToBeSacrificed:
    #     if not isReplaced(game, fieldToGrave, card):
    #         evaluate(game, sacrifice, COD.SBA, card)
    # for card in diedToSBA:
    #     if not isReplaced(game, fieldToGrave, card):
    #         evaluate(game, dies, card)
    # for card in cardsToBeDestroyed:
    #     if not isReplaced(game, fieldToGrave, card):
    #         evaluate(game, destroy, card)

    # for card in cardsToBeSacrificed:
    #     evaluate(game, fieldToGrave, card)
    # for card in cardsToBeDestroyed:
    #     evaluate(game, fieldToGrave, card)
    # for card in diedToSBA:
    #     evaluate(game, fieldToGrave, card)


def verifyLegendStatus(game, player):
    pass


def enactLegendRule(game, cards):
    # returns the set of cards to be removed selected by the player
    pass


def verifyAttachment(game, card):
    # Returns True on legal attachment False on illegal attachment
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
    totalCost = gameElements.Cost()
    totalMana = {}

    if isinstance(mainCost, dict):
        for manaType in mainCost:
            amount = mainCost[manaType]

            if manaType in totalMana:
                totalMana[manaType] += amount
            else:
                totalMana[manaType] = amount

            # If the amount of a manatype is 0 or negative, it is unneeded and can be removed from the list
            if totalMana[manaType] <= 0:
                del totalMana[manaType]
    else:
        for cost in mainCost:
            totalCost.additional.append(cost)

    if additionalCosts != []:
        for addedCost in additionalCosts:
            if isinstance(addedCost, dict):  # Do if the additional cost is a mana payment
                for manaType in addedCost:
                    amount = mainCost[manaType]

                    if manaType in totalMana:
                        totalMana[manaType] += amount
                    else:
                        totalMana[manaType] = amount

                    # If the amount of a manatype is 0 or negative, it is unneeded and can be removed from the list
                    if totalMana[manaType] <= 0:
                        del totalMana[manaType]
            else:
                totalCost.additional.append(addedCost)

    totalCost.manaCost = totalMana

    return totalCost


async def doAction(game, player):
    # waits for the player to make a choice
    player.passed = False
    player.chosenAction = None
    game.waitingOn = player

    while True:

        player.chosenAction = None
        while player.chosenAction == None and player.passed == False:
            await asyncio.sleep(0)

        if player.passed:
            game.notify("Lose Priority", {
                "gameID": game.gameID
            }, player)

            break

        else:
            game.passedInSuccession = False
            choice = player.chosenAction
            if choice[0] == 'C':
                card = game.allCards[choice]
                if card.hasType(Type.LAND):
                    gameActions.evaluate(
                        game, gameActions.playLand, card, player)
                else:
                    await declareCast(game, choice, player)
            elif choice[0] == 'A':
                await declareActivation(game, choice)


async def askBinaryQuestion(game, msg, player):
    player.answer = None
    game.notify("Binary Question", {"gameID": game.gameID, "msg": msg}, player)

    try:
        while player.answer == None:
            await asyncio.sleep(0)
    finally:
        return player.answer


async def declareCast(game, instanceID, player):
    card = game.getCard(instanceID)
    allEffects = card.effects.copy()  # copy of all effects on the card

    chosenMainCost = {}
    chosenAddedCosts = []
    chosenEffects = []  # chosen effects
    effectIndexesAdded = []  # indexes of the effects added from allEffects
    effectTypes = set()  # Effect

    result = gameElements.Effect()
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
    #         choose(game, effectList, player, InquiryType.MODAL, effectList.append(effect)))

    # # Chose what x should be
    # if Keyword.DECLARE_VAR in card.specialTypes:
    #     card.property["X"] = choose(
    #         game, None, player, InquiryType.VARIABLE, 1)

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
    card.cost = addCosts(game, card, chosenMainCost, chosenAddedCosts)

    # Add cost types to card properties like Flashback
    for costType in effectTypes:
        card.property[costType] = True

    # Evaluate cast
    if card.cost.canBePaid(game, card.controller):
        if card.cost.pay(game, card.controller):
            gameActions.evaluate(game, gameActions.cast, card)


async def declareActivation(game, abilityID):
    ability = game.GAT[abilityID]
    result = gameElements.Effect()
    result.effect = ability.effect.copy()
    result.sourceAbility = ability
    result.sourceCard = ability.source
    result.cost = addCosts(game, ability, ability.cost[0], ability.cost[1])
    result.rulesText = ability.rulesText

    if result.cost.canBePaid(game, result.sourceCard.controller):
        if await result.cost.pay(game, result.sourceCard.controller):
            gameActions.evaluate(game, gameActions.activateAbility, result)


def decideSplice(card):
    pass


def checkModifiers(game):
    pass

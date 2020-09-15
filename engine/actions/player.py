def play(game, card):
    pass


def playLand(game, card, player):
    evaluate(game, moveToZone, card=card, newZoneName=Zone.FIELD)


def cast(game, card):
    evaluate(game, moveToZone, card=card,
             newZoneName=Zone.STACK, IndexToInsert=0)


def activateAbility(game, effect):
    if effect.sourceAbility.isManaAbility:
        game.resolve(effect)
    else:
        game.push(effect)


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
                    gameActions.evaluate(game, gameActions.playLand, card=card, player=player)
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
        if await card.cost.pay(game, card.controller):
            gameActions.evaluate(game, gameActions.cast, card=card)


async def declareActivation(game, abilityID):
    ability = game.GAT[abilityID]
    result = gameElements.Effect()
    result.effect = ability.effect.copy()
    result.sourceAbility = ability
    result.sourceCard = ability.source
    print()
    result.cost = addCosts(game, ability, ability.cost[0], ability.cost[1])
    result.rulesText = ability.rulesText

    if result.cost.canBePaid(game, result.sourceCard.controller):
        if await result.cost.pay(game, result.sourceCard.controller):
            gameActions.evaluate(game, gameActions.activateAbility, effect=result)


def choose(game, options, player, inquiryType, numOfChoices):
    pass


def order(options, player):
    if(len(options) == 1):
        return options[0]
    pass

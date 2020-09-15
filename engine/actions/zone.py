def drawCard(game, player):
    """Selected player draws a card

    Args:
        game (Game): Game Object
        player (Player): Player that needs more gas

    Returns:
        None
    """
    card = player.getTopOfDeck()
    evaluate(game, moveToZone, card=card, newZoneName=Zone.HAND)


def drawCards(game, player, numToDraw):
    """Draw multiple cards

    Args:
        game (Game): Game Object
        player (Player): Player that is drawing the cards
        numToDraw (Int): Number of cards to draw

    Returns:
        None
    """
    for _ in range(numToDraw):
        evaluate(game, drawCard, player=player)


def mill(game, player):
    """Selected player mills one card

    Args:
        game (Game): Game Object
        player (Player): Player that is milling cards

    Returns:
        None
    """
    card = player.getTopOfDeck()
    evaluate(game, moveToZone, card=card, newZoneName=Zone.GRAVE)


def millCards(game, player, numToMill):
    """Mill multiple cards

    Args:
        game (Game): Game Object
        player (Player): Player that is milling cards
        numToDraw (Int): Number of cards to mill

    Returns:
        None
    """
    for _ in range(numToMill):
        evaluate(game, mill, player=player)


def phaseIn(game, activePlayer):
    """Phases in all cards the activePlayer controls.

    Args:
        game (Game): Game Object
        activePlayer(Player): The active player

    Returns:
        None
    """
    pass


def phaseOut(game, card):
    """Phases out a card.

    Args:
        game (Game): Game Object
        card(Card): Card to be phased out

    Returns:
        None
    """
    pass


def discardCard(game, card):
    pass


def discardCards(game, cardsToDiscard):
    pass


def discardToHandSize(game, player):
    pass


def gainControl(game, card, newController):
    pass


def moveToZone(game, card, newZoneName, indexToInsert=None):
    oldZoneName = str(card.currentZone)
    if card.currentZone == Zone.STACK or card.currentZone == Zone.FIELD:
        oldZone = game.zones[card.currentZone]
    else:
        oldZone = game.zones[card.controller][card.currentZone]

    if newZoneName == Zone.STACK or newZoneName == Zone.FIELD:
        newZone = game.zones[newZoneName]
    elif newZoneName == Zone.DECK:
        newZone = game.zones[card.controller][Zone.DECK]
    else:
        newZone = game.zones[card.controller][newZoneName]

    card.reset()
    oldZone.remove(card)

    if newZoneName == Zone.DECK or newZoneName == Zone.STACK:
        newZone.insert(indexToInsert, card)
    else:
        newZone.add(card)

    card.currentZone = newZoneName
    game.applyModifiers(card)

    game.notifyAll("Remove Object", {
        "gameID": game.gameID,
        "controller": card.controller.playerID,
        "instanceID": card.instanceID,
        "zone": oldZoneName})

    abilities = [[ability.abilityID, ability.rulesText]
                 for ability in card.abilities if (newZoneName in ability.allowedZones)]
    types = [str(typ) for typ in card.cardTypes]

    msg2 = {
        "gameID": game.gameID,
        "instanceID": card.instanceID,
        "name": card.name,
        "oracle": card.oracle,
        "tapped": card.tapped,
        "memID": card.memID,
        "power": card.power,
        "toughness": card.toughness,
        "controller": card.controller.playerID,
        "abilities": abilities,
        "types": types,
        "zone": str(newZoneName)
    }

    if oldZoneName == "Zone.HAND" or oldZoneName == "Zone.EXILE" or oldZoneName == "Zone.GRAVE" or oldZoneName == "Zone.DECK":
        game.notifyAll("Zone Size Update", {
            "gameID": game.gameID,
            "playerID": card.controller.playerID,
            "zoneType": str(oldZoneName),
            "num": len(oldZone)
        })

    if newZoneName == Zone.HAND or newZoneName == Zone.EXILE or newZoneName == Zone.GRAVE or newZoneName == Zone.DECK:
        game.notifyAll("Zone Size Update", {
            "gameID": game.gameID,
            "playerID": card.controller.playerID,
            "zoneType": str(newZoneName),
            "num": len(newZone)
        })

    if newZoneName == Zone.HAND or newZoneName == Zone.DECK:
        game.notify("New Object", msg2, card.controller)
    else:
        game.notifyAll("New Object", msg2)

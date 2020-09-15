def emptyManaPools(game):
    """Remove all mana from all player's mana pool. Used during step changes

    Args:
        game (Game): Game Object

    Returns:
        None
    """
    colors = {Color.WHITE, Color.BLUE, Color.BLACK,
              Color.RED, Color.GREEN, Color.COLORLESS}
    for player in game.players:
        for color in colors:
            removeAllMana(game, player, color)


def removeAllMana(game, player, color):
    """Remove all mana of a certain color in player's mana pool.

    Args:
        game (Game): Game Object
        player(Player): Player to remove mana from
        color(enumeratedTypes.Color): Color of mana to remove

    Returns:
        None
    """
    player.manaPool[color] = 0


def removeMana(game, player, color, amount):
    """Remove mana from player's mana pool.

    Args:
        game (Game): Game Object
        player(Player): Player to remove mana from
        color(enumeratedTypes.Color): Color of mana
        amount (Int): Amount of mana to remove

    Returns:
        None
    """

    player.manaPool[color] -= amount

    total = 0
    for color in player.manaPool:
        total += player.manaPool[color]

    game.notify("Mana Update", {
        "gameID": game.gameID,
        "color": str(color),
        "amount": player.manaPool[color]
    }, player)


def addMana(game, player, color, amount):
    """Add mana to player's mana pool.

    Args:
        game (Game): Game Object
        player(Player): Player to add mana
        color(enumeratedTypes.Color): Color of mana
        amount (Int): Amount of mana to add

    Returns:
        None
    """
    player.manaPool[color] += amount

    game.notify("Mana Update", {
        "gameID": game.gameID,
        "color": str(color),
        "amount": player.manaPool[color]
    }, player)


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
            if not 'action' in addedCost:  # Do if the additional cost is a mana payment
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

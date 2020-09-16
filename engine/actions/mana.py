from consts.color import Color


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

def loseLife(game, source, player, amountToLose):
    """Set the life total for selected player to (current life - the amount to lose)

    Args:
        game (Game): Game Object
        source (Card): Source of the life loss
        player (Player): Player that is loosing life
        amountToLose (Int): The amount of life to lose

    Returns:
        None
    """
    if amountToLose == 0:
        return
    player.lifeTotal -= amountToLose

    game.notifyAll("Life Total Update", {
        "gameID": game.gameID,
        "playerID": player.playerID,
        "life": player.lifeTotal
    })


def gainLife(game, source, player, amountToGain):
    """Set the life total for selected player to (current life + the amount to gain)

    Args:
        game (Game): Game Object
        source (Card): Source of the life gain
        player (Player): Player that is gaining life
        amountToGain (Int): The amount of life to gain

    Returns:
        None
    """
    if amountToGain == 0:
        return

    player.lifeTotal += amountToGain

    game.notifyAll("Life Total Update", {
        "gameID": game.gameID,
        "playerID": player.playerID,
        "life": player.lifeTotal
    })


def setLife(game, source, player, newTotal):
    """Sets the life total of the selected player to the specified amount

    Args:
        game (Game): Game Object
        source (Object): Source that is setting the player's life total
        player (Player): Player is having their life total set
        newTotal (Int): New life total

    Returns:
        None
    """
    if player.getLife() == newTotal:
        pass
    elif (player.getLife() > newTotal):
        evaluate(game, loseLife, source=source, player=player, amountToLose=(player.getLife() - newTotal))
    else:
        evaluate(game, gainLife, source=source, player=player, amountToGain=(newTotal - player.getLife()))

from actions.evaluate import evaluate


def untap(game, card):
    """Untap card

    Args:
        game (Game): Game Object
        card (Card): Card to untap

    Returns:
        None
    """
    card.tapped = False
    game.notifyAll("Untap", card.instanceID)


def untapCards(game, cardsToUntap):
    """Untap multiple cards

    Args:
        game (Game): Game Object
        cardsToUntap (List(Card)): Cards to untap

    Returns:
        None
    """
    for card in cardsToUntap:
        evaluate(game, untap, card=card)


def untapAll(game, activePlayer):
    """Untap all cards controlled by the active player during the Untap step

    Args:
        game (Game): Game Object
        activePlayer (Player): Player whose cards need to be untapped

    Returns:
        None
    """
    for card in activePlayer.getField():
        evaluate(game, untap, card=card)


def tap(game, card):
    """Tap card

    Args:
        game (Game): Game Object
        card (Card): Card to tap

    Returns:
        None
    """
    card.tapped = True

    game.notifyAll("Tap", {
        "gameID": game.gameID,
        "instanceID": card.instanceID
    })


def tapCards(game, cardsToTap):
    """Tap multiple cards

    Args:
        game (Game): Game Object
        cardsToTap (List(Card)): Cards to tap

    Returns:
        None
    """
    for card in cardsToTap:
        evaluate(game, tap, card=card)


def attach(game, source, target):
    """Attach card to another card.

    Args:
        game (Game): Game Object
        source(Card): The attachment
        target(Card): The target for the attachment

    Returns:
        None
    """
    pass


def unattach(game, attachment, target):
    """Unattach card from another card.

    Args:
        game (Game): Game Object
        source(Card): The attachment
        target(Card): The attached card

    Returns:
        None
    """
    pass


def transform(game, card):
    pass

def sacrifice(game, source, card):
    """Sacrifices the target card.

    Args:
        game (Game): Game Object
        source (Object): Spell or Ability source
        target (Card): Card to sacrifice

    Returns:
        None
    """
    evaluate(game, dies, card=card)
    evaluate(game, moveToZone, card=card, newZoneName=Zone.GRAVE)


def sacrificeCards(game, cardsToSacrifice):
    pass


def destroy(game, source, card):
    """Destroy target card.

    Args:
        game (Game): Game Object
        source (Object): Spell or Ability source
        target (Card): Card to destroy

    Returns:
        None
    """
    evaluate(game, moveToZone, card=card, newZoneName=Zone.GRAVE)


def destroyCards(game, source, cardsToBeDestroyed):
    """Destroy multiple cards.

    Args:
        game (Game): Game Object
        source (Object): Spell or Ability source
        target (Card): Cards to destroy

    Returns:
        None
    """
    legalCards = set()
    for card in cardsToBeDestroyed:
        if isLegal(game, destroy, source, card) and not isReplaced(game, destroy, source, card):
            legalCards.add(card)
    for card in legalCards:
        evaluate(game, dies, card=card)
    for card in legalCards:
        evaluate(game, destroy, source=source, card=card)

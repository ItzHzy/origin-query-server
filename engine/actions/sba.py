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

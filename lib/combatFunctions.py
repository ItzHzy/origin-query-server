import gameElements
import asyncio
from enumeratedTypes import *  # pylint: disable=unused-wildcard-import
import gameActions


def markDamage(game, source, target, amountToMark):
    """Marks creature with damage.

    Args:
        game (Game): Game State
        source (Card): Source that is causing the marked damage
        target (Card): Card that is being marked with damage
        amountToMark (int): The amount of damage to mark on a creature

    Returns:
        None
    """
    target.damageMarked += amountToMark


def removeAllDamage(game):
    for player in game.players:
        for card in player.getField():
            card.damageMarked = 0


def removeDamage(game, source, target):
    """Removes all damage marked on card

    Args:
        game (Game): Game state object
        source (Object): The object that is removing the damage
        target (Card): Creature to remove all damage from

    Returns:
        None
    """
    target.damageMarked = 0


def dealDamage(game, source, target, amountToDeal):
    """Deals Damage to target depending in its type

    Args:
        game (Game): Game state object
        source (Card): Creature source that is dealing the damage
        target (Object): Creature or Player that is being dealt damage
        amountToDeal (int): The amount of damage to deal to the target

    Returns:
        None
    """
    if isinstance(target, gameElements.Card):
        markDamage(game, source, target, amountToDeal)
    elif isinstance(target, gameElements.Player):
        gameActions.loseLife(game, source, target, amountToDeal)


def dealCombatDamage(game, source, target, amountToDeal):
    """Deals combat damage to the target.

    Args:
        game (Game): Game state object
        source (Card): Card that is dealing the combat damage
        target (Card or Player): Target that is taking the damage
        amountToDeal (Int): Amount of combat damage to deal to target
    """
    gameActions.evaluate(game, dealDamage, source, target, amountToDeal)


def dealNonCombatDamage(game, source, target, amountToDeal):
    """Deals Non-Combat to the target.

    Args:
        game (Game): Game state object
        source (Card): Source that is dealing the damage
        target (Card or Player): Target that is taking the damage
        amountToDeal (Int): Amount of damage to deal to target
    """
    gameActions.evaluate(game, dealDamage, source, target, amountToDeal)


async def chooseAttackers(game, activePlayer):
    while True:
        activePlayer.answer = None

        game.notify("Choose Attacks", {}, activePlayer)
        await asyncio.sleep(0)

        while activePlayer.answer == None:
            await asyncio.sleep(0)

        lst = []
        for index, declaration in enumerate(activePlayer.answer):
            if declaration[1][0] == "P":
                attacker = game.allCards(declaration[0])
                defender = game.findPlayer(declaration[1])
            else:
                attacker = game.allCards(declaration[0])
                defender = game.findPlayer(declaration[1])

            lst[index] = [attacker, defender]

        if declareAttackers(game, lst):
            return


async def chooseBlockers(game, player):
    while True:
        player.answer = None

        game.notify("Choose Blocks", {}, player)
        await asyncio.sleep(0)

        while player.answer == None:
            await asyncio.sleep(0)

        lst = []
        for index, declaration in enumerate(player.answer):
            blocker = game.allCards(declaration[0])
            blocked = game.allCards(declaration[1])

            lst[index] = [blocker, blocked]

        if declareBlockers(game, lst):
            return


def declareAttackers(game, listOfAttackers):
    """Used to check if all chosen attacks are legal.
       If attacks are legal, set all the attackers as attacking and
       sets the declared defender. Tiggers "on attack" abilities

    Args:
        game (Game): Game state object
        listOfAttackers (List): List of tuples of type
        Card * Object, where Card is the declared attacker and Object is
        the defending Object.

    Returns:
        True if all declared attacks are legal.
        False if any declared attacks are illegal.

    """
    for declaration in listOfAttackers:
        if gameActions.isLegal(attack, declaration[0], declaration[1]) != GameRuleAns.ALLOWED:
            return False

    for declaration in listOfAttackers:
        if isinstance(declaration[1], gameElements.Player):
            declaration[1].isDefending = True
        else:
            declaration[1].getController().isDefending = True
        declaration[0].isAttacking = True
        declaration[0].attacking = declaration[1]

    matrix = game.COMBAT_MATRIX
    for declaration in listOfAttackers:
        matrix[declaration[0]] = {
            "Assignable Damage": calculatePossibleDamage(game, declaration[0]),
            "Blockers": [],
            "Defender": declaration[1]
        }
        gameActions.evaluate(attack, game, declaration[0], declaration[1])

    return True


def declareBlockers(game, listOfBlockers):
    """Used to check if all chosen blocks are legal

    Args:
        game (Game): Game state object
        listOfBlockers (List): List of tuples of type Card * Card where Card 1
        is the declared blocker and Card 2 is the Card being blocked.

    Returns:
        True if all declared blocks are legal.
        False if any declared blocks are illegal.

    """
    for declaration in listOfBlockers:
        if gameActions.isLegal(block, declaration[0], declaration[1]) != GameRuleAns.ALLOWED:
            return False

    for declaration in listOfBlockers:
        declaration[0].isBlocking = True
        declaration[0].blocking = declaration[1]

    matrix = game.COMBAT_MATRIX
    for declaration in listOfBlockers:
        matrix[declaration[0]]["Blockers"].append(declaration[1])
        gameActions.evaluate(block, game, declaration[0], declaration[1])

    return True


def attack(game, attacker, defender):
    """Used to trigger "When ~ attacks" abilities

    Args:
        game (Game): Game state object
        attacker (Card): Creature that is doing the attacking
        defender (Object): Player or Planeswalker being targeted for the attack

    Returns:
        None
    """
    pass


def block(game, blocker, blocked):
    """Used to trigger "When ~ blocks" or "When ~ is blocked" abilities

    Args:
        game (Game): Game state object
        attacker (Card): Creature that is doing the attacking
        defender (Object): Player or Planeswalker being targeted for the attack

    Returns:
        None
    """
    pass


def resolveCombatMatrix_FS(game):
    matrix = game.COMBAT_MATRIX

    for attacker in matrix:
        blockers = attacker["Blockers"]
        defender = attacker["Defender"]
        if attacker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
            for blocker in blockers:
                assignDamage(game, attacker, blocker)
        for blocker in blockers:
            if blocker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
                gameActions.evaluate(game, dealCombatDamage, blocker, attacker)
        if attacker["Assignable Damage"] > 0 and attacker.hasKeyword(Keyword.TRAMPLE) and attacker.hasKeyword(Keyword.FIRST_STRIKE):
            gameActions.evaluate(game, dealCombatDamage, attacker,
                                 defender, attacker["Assignable Damage"])


def resolveCombatMatrix(game):
    matrix = game.COMBAT_MATRIX

    for attacker in matrix:
        blockers = attacker["Blockers"]
        defender = attacker["Defender"]
        if not attacker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
            for blocker in blockers:
                assignDamage(game, attacker, blocker)
        for blocker in blockers:
            if not blocker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
                gameActions.evaluate(game, dealCombatDamage, blocker, attacker)
        if attacker["Assignable Damage"] > 0 and attacker.hasKeyword(Keyword.TRAMPLE) and (not blocker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE)):
            gameActions.evaluate(game, dealCombatDamage, attacker,
                                 defender, attacker["Assignable Damage"])

    game.COMBAT_MATRIX = {}


def calculatePossibleDamage(game, card):
    return card.power


def assignDamage(game, source, target):
    matrix = game.COMBAT_MATRIX
    damageForLethal = target.toughness
    if matrix[source]["Assignable Damage"] >= damageForLethal:
        gameActions.evaluate(game, dealCombatDamage,
                             source, target, damageForLethal)
    elif matrix[source]["Assignable Damage"] > 0:
        gameActions.evaluate(game, dealCombatDamage, source, target,
                             matrix[source]["Assignable Damage"])
        matrix[source]["Assignable Damage"] = 0

    # Has to call dealCombatDamage
    pass


def fight(game, source, target):
    pass


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(#@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&#(((##@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&%######((####((((@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@%(####################(###((#(@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@&(((#(#######################((##&@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@##(###(######%%#################(@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@&(((#@@@@@@@@@@%%##%#%##&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@#(#@@@@@@@@@@@@%##%%%%%#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@###&@@@@@@@@@@@@%##%%%%%#@@@@@@@@@@@@@@((((//@@#***@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@####@@@@@@@@@@@@@%%%%%%%%@@@@@@@@@@@@@@@//((///*****%@@@@@@@@@@@@@
# @@@@@@@@@@@@@@#%%#@@@@@@@@@@@@%%%%%%%%@@@@@@@@@@@@@@@@@#///**,***@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@%%%%%%%@@@@@@@@@@%%%%%%%@@@@@#(#((((((@@@@@////**(@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@%%%%%%&&%&@@@@@#%%%###@@@@###(((((#((&@@@@@*****#@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@%%&&&@@@@@@@@@%#%%###@@@@###(@@@###(@@@@@(/**//@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@&%%####@@@@@((((@@((((%@@@@@*****@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%####@@@@@#####((/(@@@@@@*,,**@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@#######@@@@@###(#(@@@@@@//**,,@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@######((#######((((((/****,@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%#######&@@@#////**/*@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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
        gameActions.evaluate(game, gameActions.loseLife, source=source, player=target, amountToLose=amountToDeal)


def dealCombatDamage(game, source, target, amountToDeal):
    """Deals combat damage to the target.

    Args:
        game (Game): Game state object
        source (Card): Card that is dealing the combat damage
        target (Card or Player): Target that is taking the damage
        amountToDeal (Int): Amount of combat damage to deal to target
    """
    gameActions.evaluate(game, dealDamage, source=source, target=target, amountToDeal=amountToDeal)


def dealNonCombatDamage(game, source, target, amountToDeal):
    """Deals Non-Combat to the target.

    Args:
        game (Game): Game state object
        source (Card): Source that is dealing the damage
        target (Card or Player): Target that is taking the damage
        amountToDeal (Int): Amount of damage to deal to target
    """
    gameActions.evaluate(game, dealDamage, source=source, target=target, amountToDeal=amountToDeal)


async def chooseAttackers(game, activePlayer):
    while True:
        activePlayer.answer = None

        game.notify("Choose Attacks", {
            "gameID": game.gameID,
            "legalTargets": [{
                    "playerID": player.playerID,
                    "name": player.name
                    } for player in game.getOpponents(activePlayer)]
        }, activePlayer)
        await asyncio.sleep(0)

        while activePlayer.answer == None:
            await asyncio.sleep(0)

        declaredAttacks = {}

        for attacker in activePlayer.answer:

            if str(activePlayer.answer[attacker])[0] == "P":
                defender = game.findPlayer(activePlayer.answer[attacker])
            else:
                defender = game.allCards[activePlayer.answer[attacker]]

            declaredAttacks[game.allCards[attacker]] = defender

        if declareAttackers(game, declaredAttacks):
            return


async def chooseBlockers(game, player):
    while True:
        player.answer = None

        game.notify("Choose Blocks", {
            "gameID": game.gameID,
            "legalTargets": [{
                    "instanceID": attacker.instanceID,
                    "name": attacker.name
                    } for attacker in game.COMBAT_MATRIX]
        }, player)

        await asyncio.sleep(0)

        while player.answer == None:
            await asyncio.sleep(0)

        declaredBlocks = {}
        for blocker in player.answer:
            declaredBlocks[game.allCards[blocker]] = []

            for blocked in player.answer[blocker]:
                declaredBlocks[game.allCards[blocker]
                               ] += game.allCards(blocked)

        if declareBlockers(game, declaredBlocks):
            return


def declareAttackers(game, declaredAttacks):
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

    # Check if the declared attacks are legal
    for attacker in declaredAttacks:
        defender = declaredAttacks[attacker]
        if not gameActions.isLegal(game, attack, attacker, defender):
            return False

    # Set combat statuses for creatures and players
    for attacker in declaredAttacks:
        defender = declaredAttacks[attacker]
        if isinstance(defender, gameElements.Player):
            defender.isDefending = True
        else:
            defender.getController().isDefending = True
        attacker.isAttacking = True
        attacker.attacking = defender

    for attacker in declaredAttacks:
        defender = declaredAttacks[attacker]

        gameActions.evaluate(game, attack, attacker=attacker, defender=defender)

    return True


def declareBlockers(game, declaredBlocks):
    """Used to check if all chosen blocks are legal

    Args:
        game (Game): Game state object
        listOfBlockers (List): List of tuples of type Card * Card where Card 1
        is the declared blocker and Card 2 is the Card being blocked.

    Returns:
        True if all declared blocks are legal.
        False if any declared blocks are illegal.

    """
    for blocker in declaredBlocks:
        for blocked in declaredBlocks[blocker]:
            if not gameActions.isLegal(block, blocker, blocked):
                return False

    for blocker in declaredBlocks:
        blocker.isBlocking = True
        for blocked in declaredBlocks[blocker]:
            blocker.blocking.append(blocked)

    for blocker in declaredBlocks:
        for blocked in declaredBlocks[blocker]:
            gameActions.evaluate(game, block, blocker=blocker, blocked=blocked)

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
    game.COMBAT_MATRIX[attacker] = {
        "Assignable Damage": calculatePossibleDamage(game, attacker),
        "Blockers": [],
        "Defender": defender
    }


def block(game, blocker, blocked):
    """Used to trigger "When ~ blocks" or "When ~ is blocked" abilities

    Args:
        game (Game): Game state object
        attacker (Card): Creature that is doing the attacking
        defender (Object): Player or Planeswalker being targeted for the attack

    Returns:
        None
    """
    game.COMBAT_MATRIX[blocked]["Blockers"].append(blocker)


def resolveCombatMatrix_FS(game):
    matrix = game.COMBAT_MATRIX

    for attacker in matrix:
        blockers = game.COMBAT_MATRIX[attacker]["Blockers"]
        defender = game.COMBAT_MATRIX[attacker]["Defender"]

        if blockers != []:
            if attacker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
                for blocker in blockers:
                    damageToDeal = assignDamage(game, attacker, blocker)
                    if damageToDeal > 0:
                        gameActions.evaluate(game, dealCombatDamage, source=attacker, target=blocker, amountToDeal=damageToDeal)

            for blocker in blockers:
                if blocker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
                    gameActions.evaluate(game, dealCombatDamage, source=blocker, target=attacker, amountToDeal=calculatePossibleDamage(game, blocker))

            if game.COMBAT_MATRIX[attacker]["Assignable Damage"] > 0 and attacker.hasKeyword(Keyword.TRAMPLE) and attacker.hasKeyword(Keyword.FIRST_STRIKE):
                gameActions.evaluate(game, dealCombatDamage, source=attacker, target=defender, amountToDeal=game.COMBAT_MATRIX[attacker]["Assignable Damage"])

        elif attacker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
            gameActions.evaluate(game, dealCombatDamage, source=attacker, target=defender, amountToDeal=game.COMBAT_MATRIX[attacker]["Assignable Damage"])


def resolveCombatMatrix(game):
    matrix = game.COMBAT_MATRIX

    for attacker in matrix:
        blockers = game.COMBAT_MATRIX[attacker]["Blockers"]
        defender = game.COMBAT_MATRIX[attacker]["Defender"]

        if blockers != []:
            if not attacker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
                for blocker in blockers:
                    damageToDeal = assignDamage(game, attacker, blocker)
                    if damageToDeal > 0:
                        gameActions.evaluate(game, dealCombatDamage, source=attacker, target=blocker, amountToDeal=damageToDeal)

            for blocker in blockers:
                if not blocker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
                    gameActions.evaluate(game, dealCombatDamage, source=blocker, target=attacker, amountToDeal=calculatePossibleDamage(game, blocker))

            if game.COMBAT_MATRIX[attacker]["Assignable Damage"] > 0 and attacker.hasKeyword(Keyword.TRAMPLE) and (not blocker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE)):
                gameActions.evaluate(game, dealCombatDamage, source=attacker, target=defender, amountToDeal=game.COMBAT_MATRIX[attacker]["Assignable Damage"])

        elif not attacker.hasKeyword(Keyword.FIRST_STRIKE) or attacker.hasKeyword(Keyword.DOUBLE_STRIKE):
            gameActions.evaluate(game, dealCombatDamage, source=attacker, target=defender, amountToDeal=game.COMBAT_MATRIX[attacker]["Assignable Damage"])

    game.COMBAT_MATRIX = {}


def calculatePossibleDamage(game, card):
    return card.power


def assignDamage(game, attacker, defender):
    damageForLethal = defender.toughness
    if game.COMBAT_MATRIX[attacker]["Assignable Damage"] >= damageForLethal:
        game.COMBAT_MATRIX[attacker]["Assignable Damage"] -= damageForLethal
        return damageForLethal
    elif game.COMBAT_MATRIX[attacker]["Assignable Damage"] > 0:
        assignedDamage = game.COMBAT_MATRIX[attacker]["Assignable Damage"]
        game.COMBAT_MATRIX[attacker]["Assignable Damage"] = 0
        return assignedDamage

    return 0


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

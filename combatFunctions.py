from gameElements import * # pylint: disable=unused-wildcard-import
from enumeratedTypes import * # pylint: disable=unused-wildcard-import
from gameActions import * # pylint: disable=unused-wildcard-import

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
    pass

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
    if isinstance(target, Card):
        markDamage(game, source, target, amountToDeal)
    elif isinstance(target, Player):
        loseLife(game, source, target, amountToDeal)

def dealCombatDamage(game, source, target, amountToDeal):
    """Deals combat damage to the target.

    Args:
        game (Game): Game state object
        source (Card): Card that is dealing the combat damage
        target (Card or Player): Target that is taking the damage
        amountToDeal (Int): Amount of combat damage to deal to target
    """
    evaluate(game, dealDamage, source, target, amountToDeal)

def dealNonCombatDamage(game, source, target, amountToDeal):
    """Deals Non-Combat to the target.

    Args:
        game (Game): Game state object
        source (Card): Source that is dealing the damage
        target (Card or Player): Target that is taking the damage
        amountToDeal (Int): Amount of damage to deal to target
    """
    evaluate(game, dealDamage, source, target, amountToDeal)

def chooseAttackers(game, activePlayer):
    pass

def chooseBlockers(game, player):
    pass

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
        GameRuleAns.ALLOWED if all declared attacks are legal.
        GameRuleAns.DENIED if any declared attacks are illegal.

    """
    for declaration in listOfAttackers:
        if isLegal(attack.__name__, declaration[0], declaration[1]) != GameRuleAns.ALLOWED:
            return GameRuleAns.DENIED

    for declaration in listOfAttackers:
        declaration[0].property["isAttacking"] = True
        declaration[0].property["Attacking"] = declaration[1]

    for declaration in listOfAttackers:
        evaluate(attack, game, declaration[0], declaration[1])
    return GameRuleAns.ALLOWED

def declareBlockers(game, listOfBlockers):
    """Used to check if all chosen blocks are legal

    Args:
        game (Game): Game state object
        listOfBlockers (List): List of tuples of type Card * Card where Card 1
        is the declared blocker and Card 2 is the Card being blocked.

    Returns:
        GameRuleAns

    """
    for declaration in listOfBlockers:
        if isLegal(block.__name__, declaration[0], declaration[1]) != GameRuleAns.ALLOWED:
            return GameRuleAns.DENIED

    for declaration in listOfBlockers:
        declaration[0].property["isBlocking"] = True
        declaration[0].property["Blocking"] = declaration[1]
        declaration[1].property["Blocked"] = True

    for declaration in listOfBlockers:
        evaluate(block, game, declaration[0], declaration[1])
    return GameRuleAns.ALLOWED

def attack(game, attacker, defender):
    """Used to trigger "When ~ attacks" abilities

    Args:
        game (Game): Game state object
        attacker (Card): Creature that is doing the attacking
        defender (Object): Player or Planeswalker being targeted for the attack

    Returns:
        None
    """
    return None

def block(game, blocker, blocked):
    """Used to trigger "When ~ blocks" or "When ~ is blocked" abilities

    Args:
        game (Game): Game state object
        attacker (Card): Creature that is doing the attacking
        defender (Object): Player or Planeswalker being targeted for the attack

    Returns:
        None
    """
    return None

def resolveCombatMatrix_FS(game):
    matrix = game.GD("GLOBAL_COMBAT_MATRIX")

    for attacker in matrix:
        blockers = attacker[2]
        defender = attacker[3]
        if attacker.hasKeyword(Keyword.FIRST_STRIKE):
            for blocker in blockers:
                attacker[1] = assignDamage(game, attacker, blocker)
        for blocker in blockers:
            if blocker.hasKeyword(Keyword.FIRST_STRIKE):
                evaluate(game, dealCombatDamage, blocker, attacker)
        if attacker[1] > 0 and attacker.hasKeyword(Keyword.TRAMPLE):
            evaluate(game, dealCombatDamage, attacker, defender)

def resolveCombatMatrix(game):
    matrix = game.GD("GLOBAL_COMBAT_MATRIX")

    for attacker in matrix:
        blockers = attacker[2]
        defender = attacker[3]
        if not attacker.hasKeyword(Keyword.FIRST_STRIKE):
            for blocker in blockers:
                attacker[1] = assignDamage(game, attacker, blocker)
        for blocker in blockers:
            if not blocker.hasKeyword(Keyword.FIRST_STRIKE):
                evaluate(game, dealCombatDamage, blocker, attacker)
        if attacker[1] > 0 and attacker.hasKeyword(Keyword.TRAMPLE):
            evaluate(game, dealCombatDamage, attacker, defender)

def calculatePossibleDamage(game, card):
    pass

def assignDamage(game, source, target):
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

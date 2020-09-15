def endPhase(game, activePlayer, phase):
    """End the current phase

    Args:
        game (Game): Game Object
        activePlayer(Player): The Active Player
        phase(enumeratedTypes.TURN): The current phase or step to end

    Returns:
        None
    """
    emptyManaPools(game)
    for player in game.players:
        player.passed = False


def beginPhase(game, activePlayer, phase):
    """Begin a new phase

    Args:
        game (Game): Game Object
        activePlayer(Player): The Active Player
        phase(enumeratedTypes.TURN): The phase or step to begin

    Returns:
        None
    """
    game.currPhase = phase
    game.activePlayer = activePlayer

    msg = {
        "activePlayer": activePlayer.playerID,
        "phase": str(phase)
    }

    game.notifyAll("Start Phase", msg)


async def doPhaseActions(game):
    nextPhase = {
        Turn.UNTAP: Turn.UPKEEP,
        Turn.UPKEEP: Turn.DRAW,
        Turn.DRAW: Turn.FIRST_MAIN,
        Turn.FIRST_MAIN: Turn.BEGIN_COMBAT,
        Turn.BEGIN_COMBAT: Turn.DECLARE_ATTACKS,
        Turn.DECLARE_ATTACKS: Turn.DECLARE_BLOCKS,
        Turn.DECLARE_BLOCKS: Turn.FIRST_COMBAT_DAMAGE,
        Turn.FIRST_COMBAT_DAMAGE: Turn.SECOND_COMBAT_DAMAGE,
        Turn.SECOND_COMBAT_DAMAGE: Turn.END_COMBAT,
        Turn.END_COMBAT: Turn.SECOND_MAIN,
        Turn.SECOND_MAIN: Turn.BEGIN_END,
        Turn.BEGIN_END: Turn.CLEANUP
    }

    currPhase = game.currPhase
    activePlayer = game.activePlayer
    print(currPhase)

    if currPhase == Turn.UNTAP:
        gameActions.phaseIn(game, activePlayer)
        # checkSBA(game)
        gameActions.untapAll(game, activePlayer)
    elif currPhase == Turn.UPKEEP:
        gameActions.phaseIn(game, activePlayer)
    elif currPhase == Turn.DRAW:
        gameActions.evaluate(game, gameActions.drawCard, player=activePlayer)
    elif currPhase == Turn.DECLARE_ATTACKS:
        await combatFunctions.chooseAttackers(game, activePlayer)
    elif currPhase == Turn.DECLARE_BLOCKS:
        for player in game.getOpponents(activePlayer):
            if player.isDefending:
                await combatFunctions.chooseBlockers(game, player)
    elif currPhase == Turn.FIRST_COMBAT_DAMAGE:
        combatFunctions.resolveCombatMatrix_FS(game)
    elif currPhase == Turn.SECOND_COMBAT_DAMAGE:
        combatFunctions.resolveCombatMatrix(game)
    elif currPhase == Turn.CLEANUP:
        gameActions.discardToHandSize(game, activePlayer)
        combatFunctions.removeAllDamage(game)
        # Check for SBAs and complete loop rule 514


def goToNextPhase(game):
    currPhase = game.currPhase
    activePlayer = game.activePlayer

    gameActions.evaluate(game, gameActions.endPhase, activePlayer=activePlayer, phase=currPhase)
    if currPhase == Turn.CLEANUP and Turn.EXTRA in activePlayer.property and activePlayer.property[Turn.EXTRA] > 0:
        activePlayer.property[Turn.EXTRA] -= 1
        gameActions.evaluate(game, gameActions.beginPhase, activePlayer=activePlayer, phase=Turn.UNTAP)

    elif currPhase == Turn.CLEANUP:
        nextPlayer = game.getNextPlayer(activePlayer)
        gameActions.evaluate(game, gameActions.beginPhase, activePlayer=nextPlayer, phase=Turn.UNTAP)

    elif currPhase in activePlayer.property and activePlayer.property[currPhase] > 0:
        activePlayer.property[currPhase] -= 1
        gameActions.evaluate(game, gameActions.beginPhase, activePlayer=activePlayer, phase=currPhase)

    elif currPhase == Turn.DECLARE_ATTACKS and game.COMBAT_MATRIX == {}:
        gameActions.evaluate(game, gameActions.beginPhase, activePlayer=activePlayer, phase=Turn.END_COMBAT)
    else:
        gameActions.evaluate(game, gameActions.beginPhase, activePlayer=activePlayer, phase=nextPhase[currPhase])  # pylint: disable=unsubscriptable-object


def givePriority(game, player):
    # checkSBA(game)
    game.priority = player

    game.notify("Give Priority", {
        "gameID": game.gameID
    }, player)

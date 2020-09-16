from actions.card import untapAll
from actions.combat import removeAllDamage, resolveCombatMatrix, resolveCombatMatrix_FS, chooseAttackers, chooseBlockers
from actions.evaluate import evaluate
from actions.mana import emptyManaPools
from actions.zone import discardToHandSize, drawCard, phaseIn
from consts.turn import Turn


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
    currPhase = game.currPhase
    activePlayer = game.activePlayer
    print(currPhase)

    if currPhase == Turn.UNTAP:
        phaseIn(game, activePlayer)
        # checkSBA(game)
        untapAll(game, activePlayer)
    elif currPhase == Turn.UPKEEP:
        phaseIn(game, activePlayer)
    elif currPhase == Turn.DRAW:
        evaluate(game, drawCard, player=activePlayer)
    elif currPhase == Turn.DECLARE_ATTACKS:
        await chooseAttackers(game, activePlayer)
    elif currPhase == Turn.DECLARE_BLOCKS:
        for player in game.getOpponents(activePlayer):
            if player.isDefending:
                await chooseBlockers(game, player)
    elif currPhase == Turn.FIRST_COMBAT_DAMAGE:
        resolveCombatMatrix_FS(game)
    elif currPhase == Turn.SECOND_COMBAT_DAMAGE:
        resolveCombatMatrix(game)
    elif currPhase == Turn.CLEANUP:
        discardToHandSize(game, activePlayer)
        removeAllDamage(game)
        # Check for SBAs and complete loop rule 514


def goToNextPhase(game):
    currPhase = game.currPhase
    activePlayer = game.activePlayer

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

    evaluate(game, endPhase, activePlayer=activePlayer, phase=currPhase)
    if currPhase == Turn.CLEANUP and Turn.EXTRA in activePlayer.property and activePlayer.property[Turn.EXTRA] > 0:
        activePlayer.property[Turn.EXTRA] -= 1
        evaluate(game, beginPhase, activePlayer=activePlayer, phase=Turn.UNTAP)

    elif currPhase == Turn.CLEANUP:
        nextPlayer = game.getNextPlayer(activePlayer)
        evaluate(game, beginPhase, activePlayer=nextPlayer, phase=Turn.UNTAP)

    elif currPhase in activePlayer.property and activePlayer.property[currPhase] > 0:
        activePlayer.property[currPhase] -= 1
        evaluate(game, beginPhase, activePlayer=activePlayer, phase=currPhase)

    elif currPhase == Turn.DECLARE_ATTACKS and game.COMBAT_MATRIX == {}:
        evaluate(game, beginPhase, activePlayer=activePlayer, phase=Turn.END_COMBAT)
    else:
        evaluate(game, beginPhase, activePlayer=activePlayer, phase=nextPhase[currPhase])  # pylint: disable=unsubscriptable-object


def givePriority(game, player):
    # checkSBA(game)
    game.priority = player

    game.notify("Give Priority", {
        "gameID": game.gameID
    }, player)

from basicFunctions import * # pylint: disable=unused-wildcard-import
from enumeratedTypes import * # pylint: disable=unused-wildcard-import

def startGame(game):
    first = game.getNextPlayer()
    game.SD("Active Player", first) 

def proceedGame(game):
    stack = game.zones[Zone.STACK]
    while not game.won:
        doPhaseActions(game)
        passedInSuccession = False
        while not passedInSuccession and stack != []:
            passedInSuccession = True
            for player in game.getRelativePlayerList(game.activePlayer):
                checkSBA(game)
                givePriority(game, player)
                if choose(["Do action?"], player, InquiryType.BOOLEAN, -1):
                    passedInSuccession = False
                    while not player.passed:
                        doSomething(game, player)
                
import asyncio

from actions.evaluate import evaluate
from actions.zone import moveToZone
from consts.type import Type
from consts.zone import Zone

from elements.effect import Effect


def play(game, card):
    pass


def playLand(game, card, player):
    evaluate(game, moveToZone, card=card, newZoneName=Zone.FIELD)


def cast(game, card):
    evaluate(game, moveToZone, card=card,
             newZoneName=Zone.STACK, IndexToInsert=0)


def activateAbility(game, effect):
    if effect.sourceAbility.isManaAbility:
        game.resolve(effect)
    else:
        game.push(effect)

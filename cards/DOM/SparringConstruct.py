from gameElements import *
from combatFunctions import *
from gameActions import *
from enumeratedTypes import *


class SparringConstruct(Card):
    def __init__(self, game, player, key):
        super(SparringConstruct, self).__init__(game, player, key)

        self.manaCost = {ManaType.GENERIC: 1}

        # When ~ dies, put a +1/+1 counter on target creature you control.

        # When ~ dies,
        def f1(action, **params):
            if params["card"] == self:
                return True
            return False
        # End

        # put a +1/+1 counter on target creature you control
        r2 = "target creature you control"
        t1 = TargetRestriction(game, r2, doesTarget=True, controllers=Placeholder.YOU, zones={Zone.FIELD})
        e1 = (
            [tap, t1]
        )
        # End

        r1 = "When ~ dies, put a +1/+1 counter on target creature you control."
        a1 = TriggeredAbility(game, self, r1, gameActions.dies, f1, e1)
        # End

        self.printed = {
            "name": "Sparring Construct",
            "power": 1,
            "toughness": 1,
            "abilities": [a1],
            "types": {Type.ARTIFACT, Type.CREATURE, Subtype.CONSTRUCT},
            "colors": {Color.COLORLESS}
        }

        self.update()

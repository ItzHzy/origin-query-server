from gameElements import *
from combatFunctions import *
from gameActions import *
from enumeratedTypes import *


class DAvenantTrapper(Card):
    def __init__(self, game, player, key):
        super(DAvenantTrapper, self).__init__(game, player, key)

        self.manaCost = {ManaType.WHITE: 1, ManaType.GENERIC: 2}

        # Whenever you cast a historic spell, tap target creature an opponent controls.

        # Whenever you cast a historic spell,
        def f1(action, **params):
            if params["card"].isHistoric():
                return True
            return False
        # End

        # tap target creature an opponent controls
        r2 = "target creature an opponent controls"
        t1 = TargetRestriction(game, r2, doesTarget=True, controllers=Placeholder.OPPONENTS, zones={Zone.FIELD})
        e1 = (
            [tap, t1]
        )
        # End

        r1 = "Whenever you cast a historic spell, tap target creature an opponent controls."
        a1 = TriggeredAbility(game, self, r1, gameActions.cast, f1, e1)
        # End

        self.printed = {
            "name": "D'Avenant Trapper",
            "power": 3,
            "toughness": 2,
            "abilities": [a1],
            "types": {Type.CREATURE, Subtype.HUMAN, Subtype.ARCHER},
            "colors": {Color.WHITE}
        }

        self.update()

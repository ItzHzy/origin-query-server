from enumeratedTypes import *
from combatFunctions import *
from gameElements import *
from gameActions import *


class Plains(Card):
    def __init__(self, game, player, key):
        super(Plains, self).__init__(game, player, key)

        # AA: {T}: Add {W}

        # C: {T}
        c1 = (
            {},
            [
                {
                    'action': tap,
                    'card': self
                }
            ]
        )
        # End

        # E: Add {W}
        e1 = [
            {
                'action': addMana,
                'player': self.controller,
                'color': Color.WHITE,
                'amount': 1
            }
        ]
        # End

        r1 = f"{{T}}: Add {{W}}."
        a1 = ActivatedAbility(game, self, r1, c1, e1, allowedZones={Zone.FIELD}, isManaAbility=True)
        # End

        self.printed = {
            "name": "Plains",
            "power": 0,
            "toughness": 0,
            "abilities": [a1],
            "types": {Supertype.BASIC, Type.LAND, Subtype.PLAINS},
            "colors": {Color.COLORLESS}
        }

        self.update()

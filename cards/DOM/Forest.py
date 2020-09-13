from enumeratedTypes import *
from combatFunctions import *
from gameElements import *
from gameActions import *


class Forest(Card):
    def __init__(self, game, player, key):
        super(Forest, self).__init__(game, player, key)

        # AA: {T}: Add {F}

        # C: {T}
        c1 = ({}, [[tap, self]])
        # End

        # E: Add {G}
        e1 = [
            [addMana, self.controller, Color.GREEN, 1]
        ]
        # End

        r1 = f"{{T}}: Add {{G}}."
        a1 = ActivatedAbility(game, self, r1, c1, e1, allowedZones={Zone.FIELD}, isManaAbility=True)
        # End

        self.printed = {
            "name": "Forest",
            "power": 0,
            "toughness": 0,
            "abilities": [a1],
            "types": {Supertype.BASIC, Type.LAND, Subtype.FOREST},
            "colors": {Color.COLORLESS}
        }

        self.update()
